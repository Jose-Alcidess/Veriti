# analyzer.py
import re, time, math, os
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import spacy
from transformers import pipeline
from sqlalchemy import func
from model import SessionLocal, Client, Keyword, Mention, Analysis

nlp = spacy.load("pt_core_news_sm")

SOURCES = [
    {"name": "G1", "url": "https://g1.globo.com/", "selector": ("a", {"class":"feed-post-link"})},
    # adicione outras fontes relevantes para política/negócios
]

# Escolha de modelo (mantenha o seu como fallback)
sentiment = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

def simplify(label: str) -> str:
    estrelas = int(label[0])  # '1 star'...'5 stars'
    if estrelas <= 2: return "Negativo"
    if estrelas == 3: return "Neutro"
    return "Positivo"

def rep_score(label: str, score: float) -> float:
    m = {"Positivo": +1, "Neutro": 0, "Negativo": -1}[label]
    return m * score

def fetch_mentions():
    items = []
    for src in SOURCES:
        r = requests.get(src["url"], timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        tag, attrs = src["selector"]
        for a in soup.find_all(tag, attrs=attrs):
            title = a.get_text(strip=True)
            url = a.get("href")
            if title and url:
                items.append({"source": src["name"], "title": title, "url": url})
    return items

def relevant_for_client(title: str, keywords: list[str]) -> bool:
    tlow = title.lower()
    return any(re.search(rf"\b{re.escape(k.lower())}\b", tlow) for k in keywords)

def analyze_and_store():
    db = SessionLocal()
    try:
        mentions = fetch_mentions()
        clients = db.query(Client).filter_by(active=True).all()
        for client in clients:
            kw = [k.term for k in client.keywords]
            for m in mentions:
                if not relevant_for_client(m["title"], kw): 
                    continue
                # evitar duplicados simples
                exists = db.query(Mention).filter(
                    Mention.client_id==client.id, Mention.url==m["url"]
                ).first()
                if exists: 
                    continue
                men = Mention(
                    client_id=client.id, source=m["source"], title=m["title"], url=m["url"],
                    published_at=datetime.utcnow()
                )
                db.add(men); db.flush()
                res = sentiment(m["title"])[0]
                lab = simplify(res["label"])
                sc = rep_score(lab, float(res["score"]))
                ana = Analysis(mention_id=men.id, sentiment_label=lab, sentiment_score=float(res["score"]), rep_score=sc)
                db.add(ana)
        db.commit()
    finally:
        db.close()

def analyze_existing_mentions():
    db = SessionLocal()
    try:
        mentions = db.query(Mention).outerjoin(Analysis).filter(Analysis.id == None).all()
        for men in mentions:
            res = sentiment(men.title)[0]
            lab = simplify(res["label"])
            sc = rep_score(lab, float(res["score"]))
            ana = Analysis(
                mention_id=men.id,
                sentiment_label=lab,
                sentiment_score=float(res["score"]),
                rep_score=sc
            )
            db.add(ana)
        db.commit()
    finally:
        db.close()

def rolling_score(db, client_id: int, hours: int = 72, lam: float = 0.08):
    since = datetime.utcnow() - timedelta(hours=hours)
    q = db.query(Analysis, Mention.inserted_at).join(Mention, Mention.id==Analysis.mention_id)\
        .filter(Mention.client_id==client_id, Mention.inserted_at>=since).all()
    if not q:
        return None
    num = den = 0.0
    now = datetime.utcnow()
    for a, ts in q:
        dt = (now - ts).total_seconds()/3600.0
        w = math.exp(-lam * dt)
        num += w * a.rep_score
        den += w
    return num/den if den>0 else 0.0

# novo arquivo: analyze_mentions.py
from analyzer import analyze_existing_mentions

if __name__ == "__main__":
    analyze_existing_mentions()
