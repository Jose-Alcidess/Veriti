# report.py
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from weasyprint import HTML  # pip install weasyprint
import jinja2, os

ENGINE = create_engine(os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/reputacao"))

def fetch_data(client_id: int, hours: int = 168):
    q = text("""
        SELECT m.source, m.title, m.url, m.inserted_at, a.sentiment_label, a.rep_score
        FROM mentions m JOIN analysis a ON a.mention_id=m.id
        WHERE m.client_id=:cid AND m.inserted_at >= NOW() - INTERVAL ':h hours'
        ORDER BY m.inserted_at DESC
    """).bindparams(cid=client_id, h=hours)
    df = pd.read_sql(q, ENGINE)
    return df

def render_html(client_name: str, df: pd.DataFrame, summary: str, actions_md: str) -> str:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("./templates"))
    tpl = env.get_template("report.html")  # crie um template elegante com CSS
    pos = (df['sentiment_label']=="Positivo").sum()
    neg = (df['sentiment_label']=="Negativo").sum()
    neu = (df['sentiment_label']=="Neutro").sum()
    return tpl.render(
        client=client_name, generated_at=datetime.utcnow(),
        summary=summary, actions=actions_md,
        pos=pos, neg=neg, neu=neu,
        top_neg=df[df['sentiment_label']=="Negativo"].head(10).to_dict("records")
    )

def build_pdf(client_id: int, client_name: str, hours: int = 168, outfile: str = "relatorio.pdf"):
    df = fetch_data(client_id, hours)
    rec = pd.read_sql(f"SELECT summary, actions FROM recommendations WHERE client_id={client_id} ORDER BY created_at DESC LIMIT 1", ENGINE)
    summary = rec['summary'].iloc[0] if not rec.empty else "Sem resumo disponível."
    actions = rec['actions'].iloc[0] if not rec.empty else "Sem ações disponíveis."
    html = render_html(client_name, df, summary, actions)
    HTML(string=html).write_pdf(outfile)
    return outfile
