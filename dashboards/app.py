import streamlit as st

st.set_page_config(
    page_title='Instagram & Bem-Estar',
    page_icon='📱',
    layout='wide',
    initial_sidebar_state='collapsed'
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Space Grotesk', sans-serif; }
    .stApp { background-color: #050508; }
    [data-testid="stSidebar"] { background: #080810; border-right: 1px solid #00ff8822; }
    .block-container { padding-top: 2rem; max-width: 1200px; }
    div[data-testid="stMetric"] {
        background: #0a0a14;
        border: 1px solid #00ff8833;
        border-radius: 12px;
        padding: 16px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8em !important;
        font-weight: 700 !important;
        color: #00ff88 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #444466 !important;
        font-size: 0.8em !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    h1, h2, h3 { color: #ffffff !important; }
    [data-testid="stSidebarNav"] { display: none; }

    /* Page link buttons */
    [data-testid="stPageLink"] {
        background: transparent !important;
        border: 1px solid #00ff8844 !important;
        border-radius: 8px !important;
        color: #00ff88 !important;
        width: 100% !important;
        margin-top: 0.5rem !important;
        font-size: 0.68em !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    [data-testid="stPageLink"] p,
    [data-testid="stPageLink"] span {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        font-size: 1em !important;
        letter-spacing: 0.03em !important;
    }
    [data-testid="stPageLink"]:hover {
        background: #00ff8811 !important;
        border-color: #00ff88 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.html("""
<div style='padding: 4rem 0 2rem 0;'>
    <p style='
        color: #00ff88;
        font-size: 0.85em;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin: 0;
        font-weight: 600;
    '>Laboratório de Análise de Dados · 2025/26</p>

    <h1 style='
        font-size: 4em;
        font-weight: 700;
        color: #ffffff;
        margin: 0.2rem 0;
        line-height: 1;
        letter-spacing: -0.02em;
    '>Instagram<br><span style="color: #00ff88;">& Bem-Estar</span></h1>

    <p style='color: #333355; font-size: 1em; margin: 0.8rem 0 0 0;'>
        O Custo Psicológico das Redes Sociais · 300.000 utilizadores sintéticos
    </p>
    <div style='
        margin-top: 2rem;
        height: 1px;
        background: linear-gradient(90deg, #00ff88, transparent);
        width: 200px;
    '></div>
</div>
""")

# ── Stats strip ───────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric('Utilizadores', '300.000')
c2.metric('Variáveis', '58')
c3.metric('Dashboards', '4')
c4.metric('Novas Features', '8')

st.html("<br>")
st.html("""
<p style='
    color: #333355;
    font-size: 0.75em;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 600;
    margin-bottom: 0.5rem;
'>— Seleciona um dashboard</p>
""")

# ── Dashboard cards + navegação ───────────────────────────────
dashboards = [
    {
        'emoji': '📱',
        'titulo': 'Utilizador Comum',
        'cor': '#ffdd00',
        'historia': '"Como te comparas com o mundo?"',
        'desc': 'Define o teu perfil, descobre a tua persona e recebe recomendações.',
        'page': 'pages/1_utilizador.py',
        'label': 'Utilizador →',
    },
    {
        'emoji': '🧑‍⚕️',
        'titulo': 'Profissional de Saúde',
        'cor': '#ff6bff',
        'historia': '"Quem são os utilizadores em risco?"',
        'desc': 'Indicadores clínicos, grupos vulneráveis e notas de interpretação.',
        'page': 'pages/2_saude.py',
        'label': 'Saúde →',
    },
    {
        'emoji': '🔬',
        'titulo': 'Investigador',
        'cor': '#00ff88',
        'historia': '"Os dados revelam o que o olho não vê"',
        'desc': 'Correlações, distribuições, estatísticas avançadas e explorador de variáveis.',
        'page': 'pages/3_investigador.py',
        'label': 'Investigador →',
    },
    {
        'emoji': '📊',
        'titulo': 'Gestor de Marketing',
        'cor': '#00ddff',
        'historia': '"Onde está a atenção?"',
        'desc': 'Personas, engagement, conteúdo preferido e comportamento por mercado.',
        'page': 'pages/4_marketing.py',
        'label': 'Marketing →',
    },
]

cols = st.columns(4)
for col, d in zip(cols, dashboards):
    with col:
        st.html(f"""
        <div style='
            background: #080810;
            border: 1px solid {d["cor"]}22;
            border-bottom: 2px solid {d["cor"]};
            border-radius: 12px;
            padding: 1.5rem 1rem;
            height: 300px;
        '>
            <div style='
                font-size: 1.8em;
                margin-bottom: 0.8rem;
                filter: drop-shadow(0 0 8px {d["cor"]});
            '>{d["emoji"]}</div>
            <p style='
                color: {d["cor"]};
                font-size: 0.75em;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                font-weight: 700;
                margin: 0 0 0.3rem 0;
            '>{d["titulo"]}</p>
            <p style='
                color: #ffffff;
                font-size: 0.8em;
                font-style: italic;
                margin: 0 0 0.4rem 0;
                font-weight: 300;
            '>{d["historia"]}</p>
            <p style='color: #333355; font-size: 0.75em; margin: 0; line-height: 1.4;'>
                {d["desc"]}
            </p>
        </div>
        """)
        st.page_link(d['page'], label=d['label'], use_container_width=True)

st.html("""
<div style='margin-top: 4rem; padding-top: 1rem; border-top: 1px solid #0a0a14;'>
    <p style='color: #1a1a2e; font-size: 0.8em; text-align: center;'>
        Dataset: Social Media User Behavior & Lifestyle · Kaggle CC0 · LAD 2025/26
    </p>
</div>
""")