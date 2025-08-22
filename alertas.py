# alerts.py
import smtplib, ssl, os
from email.mime.text import MIMEText
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import pandas as pd

ENGINE = create_engine(os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/reputacao"))

def negative_spike(client_id: int, hours: int = 6, threshold: int = 5) -> bool:
    df = pd.read_sql(text("""
        SELECT a.sentiment_label FROM mentions m 
        JOIN analysis a ON a.mention_id=m.id
        WHERE m.client_id=:cid AND m.inserted_at >= NOW() - INTERVAL ':h hours'
    """).bindparams(cid=client_id, h=hours), ENGINE)
    return (df['sentiment_label']=="Negativo").sum() >= threshold

def send_email(to_email: str, subject: str, body: str):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    with smtplib.SMTP_SSL(smtp_server, 465, context=ssl.create_default_context()) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [to_email], msg.as_string())
