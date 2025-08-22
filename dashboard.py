# dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
import altair as alt
import os

#  Conexão com o banco
ENGINE = create_engine(os.getenv("DATABASE_URL", "sqlite:///monitor.db"))

#  Configuração da página
st.set_page_config(page_title="Reputação em Tempo Real", layout="wide")

# Cache de dados
@st.cache_data(ttl=120)
def load_clients():
    return pd.read_sql("SELECT id, name, segment FROM clients WHERE active = true ORDER BY name", ENGINE)

@st.cache_data(ttl=120)
def load_mentions(client_id: int, hours: int = 72):
    q = text(f"""
    SELECT m.id, m.source, m.title, m.url, m.inserted_at, a.sentiment_label, a.sentiment_score, a.rep_score
    FROM mentions m
    JOIN analysis a ON a.mention_id = m.id
    WHERE m.client_id = :cid AND m.inserted_at >= datetime('now', '-{hours} hours')
    ORDER BY m.inserted_at DESC
    """).bindparams(cid=client_id)
    return pd.read_sql(q, ENGINE)

#  Série temporal de reputação
def rep_timeseries(df: pd.DataFrame):
    if df.empty or not {'inserted_at', 'rep_score'}.issubset(df.columns):
        return pd.DataFrame(columns=['ts', 'rep_score'])
    df['ts'] = pd.to_datetime(df['inserted_at'], errors='coerce')
    g = (
        df.set_index('ts')
          .resample('1H')['rep_score']
          .mean()
          .fillna(0)
          .reset_index()
    )
    return g

# Título
st.markdown("## 🧭 Monitor de Reputação em Tempo Real")

# 👥 Seleção de cliente e janela de tempo
clients = load_clients()
col1, col2, col3 = st.columns([2,1,1])
with col1:
    client_name = st.selectbox("Cliente", clients['name'])
client_id = int(clients[clients['name']==client_name]['id'].iloc[0])
with col2:
    hours = st.slider("Janela (horas)", 24, 168, 72, step=24)
with col3:
    st.write("")
    if st.button("🔄 Atualizar agora"):
        st.cache_data.clear()

#  Carrega menções
df = load_mentions(client_id, hours)
ts = rep_timeseries(df)

#  Gráfico de reputação
st.divider()
st.subheader("📈 Evolução do Score de Reputação")
line_chart = alt.Chart(ts).mark_line(point=True).encode(
    x=alt.X('ts:T', title='Hora'),
    y=alt.Y('rep_score:Q', title='Score de Reputação'),
    tooltip=['ts', 'rep_score']
).properties(height=280)
st.altair_chart(line_chart, use_container_width=True)

#  Gráfico de sentimento
st.subheader("📊 Distribuição de Sentimento")
pie = df['sentiment_label'].value_counts().rename_axis('Sentimento').reset_index(name='Qtd')
bar_chart = alt.Chart(pie).mark_bar().encode(
    x=alt.X('Sentimento', sort='-y'),
    y='Qtd',
    color='Sentimento',
    tooltip=['Sentimento', 'Qtd']
).properties(height=280)
st.altair_chart(bar_chart, use_container_width=True)

#  Tabela de menções
st.divider()
st.subheader("📰 Menções Recentes")
st.dataframe(df[['inserted_at','source','sentiment_label','title','url']].rename(columns={
    'inserted_at':'Quando','source':'Fonte','sentiment_label':'Sentimento','title':'Título','url':'Link'
}), use_container_width=True, height=300)

# Recomendações
st.divider()
st.subheader("🧠 Recomendações")
rec = pd.read_sql(f"""
    SELECT summary, actions, created_at 
    FROM recommendations 
    WHERE client_id={client_id} 
    ORDER BY created_at DESC 
    LIMIT 1
""", ENGINE)

if rec.empty:
    st.info("⚠️ Sem recomendações geradas no período. Gere na aba Administração.")
else:
    st.success(f"📌 **Resumo:** {rec['summary'].iloc[0]}")
    st.markdown("🛠️ **Ações sugeridas:**")
    st.markdown(rec['actions'].iloc[0])

#  Administração
st.divider()
with st.expander("⚙️ Administração"):
    st.markdown("**Cadastrar termos e gerar recomendações**")
    new_term = st.text_input("Adicionar termo (palavra-chave)")
    if new_term.strip():
        if st.button("➕ Adicionar termo"):
            ENGINE.execute(text("INSERT INTO keywords (client_id, term) VALUES (:cid, :t)").bindparams(cid=client_id, t=new_term.strip()))
            st.success(f"✅ Termo '{new_term}' adicionado.")
            st.cache_data.clear()
    else:
        st.warning("Digite um termo antes de adicionar.")
    
    if st.button("⚡ Gerar recomendações agora"):
        from recomendacao import generate_recommendations
        generate_recommendations(client_id, hours=hours)
        st.success("✅ Recomendações atualizadas.")
        st.cache_data.clear()

#  Rodapé
st.markdown("---")
st.caption("Desenvolvido por Jose • Atualizado em tempo real • Powered by Streamlit & SQLAlchemy")
