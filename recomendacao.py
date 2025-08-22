# recommendations.py
from datetime import datetime, timedelta
from sqlalchemy import func
from model import SessionLocal, Client, Mention, Analysis, Recommendation

NEG_TRIGGERS_POL = ["corrupção", "escândalo", "investigação", "propina", "desvio"]
NEG_TRIGGERS_CORP = ["recall", "boicote", "falha", "vazamento", "atraso", "preço abusivo"]

def generate_recommendations(client_id: int, hours: int = 48):
    db = SessionLocal()
    try:
        client = db.query(Client).get(client_id)
        since = datetime.utcnow() - timedelta(hours=hours)
        rows = db.query(Mention.title, Analysis.sentiment_label)\
                 .join(Analysis, Analysis.mention_id==Mention.id)\
                 .filter(Mention.client_id==client_id, Mention.inserted_at>=since).all()
        neg_titles = [t for t,l in rows if l=="Negativo"]
        pos_titles = [t for t,l in rows if l=="Positivo"]

        triggers = NEG_TRIGGERS_POL if client.segment=="politico" else NEG_TRIGGERS_CORP
        hits = [t for t in neg_titles if any(k in t.lower() for k in triggers)]

        summary = f"{len(rows)} menções nas últimas {hours}h: {len(pos_titles)} positivas, {len(neg_titles)} negativas."
        actions = []

        if len(neg_titles) >= 5:
            actions.append("• Estabelecer war room de comunicação nas próximas 24h e designar porta-voz único.")
        if hits:
            if client.segment=="politico":
                actions.append("• Emitir nota objetiva sobre o tema sensível detectado, com dados verificáveis e cronologia dos fatos.")
                actions.append("• Conceder entrevista a veículo regional de alta confiança para ancorar narrativa.")
                actions.append("• Reforçar agenda positiva com entregas locais nas próximas 72h.")
            else:
                actions.append("• Publicar comunicado com reconhecimento do problema, plano de correção e prazos (SLA).")
                actions.append("• Abrir canal dedicado para atendimento de afetados e divulgar FAQ transparente.")
                actions.append("• Programar conteúdos esclarecedores nas redes com monitoramento de comentários.")
        if not actions:
            actions.append("• Manter monitoramento intensivo e preparar Q&A atualizado para porta-vozes.")
            actions.append("• Capitalizar menções positivas com cases e depoimentos públicos nas próximas 48h.")

        rec = Recommendation(
            client_id=client_id,
            window_start=since,
            window_end=datetime.utcnow(),
            summary=summary,
            actions="\n".join(actions)
        )
        db.add(rec); db.commit()
        return rec
    finally:
        db.close()
