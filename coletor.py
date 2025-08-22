# coletor_bolsonaro.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Mention  # importa sua classe Mention

# Conexão com o banco SQLite
DATABASE_URL = "sqlite:///monitor.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# URL de busca
def pessoa():
    return "Caiado"
url = f"https://g1.globo.com/busca/?q={pessoa()}"

def coletar_mencoes():
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Seleciona títulos e links
    resultados = soup.select("div.widget--info__text-container > a")
    mencoes = []
    for r in resultados:
        titulo = r.get_text(strip=True)
        link = r.get("href")
        if titulo and link:
            mencoes.append((titulo, link))
    return mencoes

def salvar_no_banco(mencoes):
    db = SessionLocal()
    try:
        for titulo, link in mencoes:
            # Evita duplicados
            existe = db.query(Mention).filter_by(url=link).first()
            if existe:
                continue
            m = Mention(
                client_id=1,  # ID do cliente que você cadastrou
                source="G1",
                title=titulo,
                url=link,
                published_at=datetime.utcnow(),
                inserted_at=datetime.utcnow()
            )
            db.add(m)
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    mencoes = coletar_mencoes()
    print(f"Coletadas {len(mencoes)} menções sobre ({pessoa()})")
    salvar_no_banco(mencoes)
    print("Menções salvas no banco com sucesso!")
