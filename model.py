# models.py
from datetime import datetime
from sqlalchemy import (create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///monitor.db")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    segment = Column(String(100))  # ex.: "politico", "empresa"
    active = Column(Boolean, default=True)
    keywords = relationship("Keyword", back_populates="client")

class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    term = Column(String(200), index=True, nullable=False)
    client = relationship("Client", back_populates="keywords")

class Mention(Base):
    __tablename__ = "mentions"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, index=True)
    source = Column(String(200))
    title = Column(Text, nullable=False)
    url = Column(Text)
    published_at = Column(DateTime, default=datetime.utcnow)
    inserted_at = Column(DateTime, default=datetime.utcnow, index=True)

class Analysis(Base):
    __tablename__ = "analysis"
    id = Column(Integer, primary_key=True)
    mention_id = Column(Integer, ForeignKey("mentions.id"))
    sentiment_label = Column(String(20))  # Positivo/Neutro/Negativo
    sentiment_score = Column(Float)       # 0..1 confiança
    rep_score = Column(Float)             # score de reputação da menção (-1..+1)
    created_at = Column(DateTime, default=datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, index=True)
    window_start = Column(DateTime)
    window_end = Column(DateTime)
    summary = Column(Text)    # resumo do período
    actions = Column(Text)    # lista de ações sugeridas (markdown)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)
if __name__ == "__main__":
    init_db()
    print("Banco de dados e tabelas criados com sucesso!")
