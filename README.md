# Veriti - Monitor de Reputação e Gestão de Crise

O **Veriti** é uma plataforma de inteligência de dados focada em monitoramento de reputação em tempo real. O sistema coleta menções na mídia, analisa o sentimento utilizando modelos de NLP (Processamento de Linguagem Natural), calcula scores de reputação e gera recomendações estratégicas automáticas para gestão de crises políticas e corporativas.

## 🚀 Funcionalidades

- **Coleta Automática**: Monitoramento de portais de notícias (ex: G1) em busca de palavras-chave definidas por cliente.
- **Análise de Sentimento com IA**: Classificação automática (Positivo, Neutro, Negativo) utilizando Transformers (`bert-base-multilingual-uncased-sentiment`).
- **Score de Reputação**: Cálculo de índice de reputação ponderado pelo tempo (rolling score).
- **Dashboard Interativo**: Visualização em tempo real com Streamlit (Gráficos de tendência, distribuição de sentimento e feed de notícias).
- **Sistema de Alertas**: Detecção de picos negativos ("Negative Spikes") com envio de e-mail.
- **Recomendações Estratégicas**: Sugestão automática de ações (ex: "Estabelecer War Room", "Emitir Nota") baseada no volume e teor das menções.
- **Relatórios PDF**: Geração de relatórios executivos prontos para impressão.

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.9+
- **Web Framework**: Streamlit
- **Banco de Dados**: SQLAlchemy (SQLite para dev, PostgreSQL para prod)
- **NLP & ML**: Hugging Face Transformers, Spacy, PyTorch
- **Scraping**: BeautifulSoup4, Requests
- **Agendamento**: APScheduler
- **Relatórios**: Jinja2, WeasyPrint

## 📦 Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/veriti.git
   cd veriti
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências**:
   ```bash
   pip install pandas sqlalchemy streamlit altair requests beautifulsoup4 spacy transformers torch weasyprint apscheduler jinja2 psycopg2-binary
   ```

4. **Baixe o modelo de linguagem do Spacy**:
   ```bash
   python -m spacy download pt_core_news_sm
   ```

## ⚙️ Configuração

Crie um arquivo `.env` ou configure as variáveis de ambiente (opcional, o padrão é SQLite local):

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/reputacao
SMTP_SERVER=smtp.gmail.com
SMTP_USER=seu_email@gmail.com
SMTP_PASS=sua_senha_app
```

## 🏃‍♂️ Como Executar

### 1. Inicializar o Banco de Dados
Antes da primeira execução, crie as tabelas:

```bash
python model.py
```

### 2. Iniciar o Coletor e Analisador (Backend)
Para rodar o agendador que coleta notícias e analisa sentimentos em segundo plano:

```bash
python agendar.py
```

### 3. Iniciar o Dashboard (Frontend)
Para visualizar os dados:

```bash
streamlit run dashboard.py
```
O dashboard estará disponível em `http://localhost:8501`.

## 📂 Estrutura do Projeto

| Arquivo | Descrição |
|---------|-----------|
| `analyzer.py` | Core de análise: scraping, NLP (BERT) e cálculo de scores. |
| `dashboard.py` | Interface visual feita em Streamlit. |
| `model.py` | Definição do esquema do banco de dados (ORM). |
| `recomendacao.py` | Lógica de negócios para gerar sugestões de gestão de crise. |
| `report.py` | Gerador de relatórios em PDF/HTML. |
| `alertas.py` | Lógica de disparo de e-mails para picos negativos. |
| `agendar.py` | Scheduler para rodar tarefas recorrentes. |
| `coletor.py` | Script auxiliar de coleta específica. |

## 🛡️ Aviso Legal

Este software realiza *web scraping* de fontes públicas de notícias. Certifique-se de respeitar os termos de serviço (`robots.txt`) dos sites monitorados e utilizar os dados de acordo com a LGPD e leis vigentes.

---

**Desenvolvido por Jose**
```

<!--
[PROMPT_SUGGESTION]Como eu crio um arquivo requirements.txt baseado nos imports desses arquivos?[/PROMPT_SUGGESTION]
[PROMPT_SUGGESTION]Adicione uma funcionalidade no dashboard.py para permitir o download do relatório em PDF gerado pelo report.py[/PROMPT_SUGGESTION]
