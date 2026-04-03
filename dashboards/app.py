# ============================================================
# APP.PY — Entrada principal do Dashboard
# ============================================================
import streamlit as st

st.set_page_config(
    page_title='📱 Instagram & Bem-Estar',
    page_icon='📱',
    layout='wide',
    initial_sidebar_state='expanded'
)

# CSS global (NOVA PALETA)
st.markdown("""
<style>
    .main { background-color: #0a0a0f; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111118 0%, #0a0a0f 100%);
    }

    .stMetric {
        background: linear-gradient(135deg, #111118, #1c1c28);
        border-radius: 10px;
        padding: 10px;
        border-left: 3px solid #c850c0;
    }

    div[data-testid="stMetricValue"] {
        color: #f0f0f5;
        font-size: 1.4em;
    }

    div[data-testid="stMetricLabel"] {
        color: #8888aa;
    }

    hr {
        border-color: #2a2a3e;
    }
</style>
""", unsafe_allow_html=True)

# ── Página inicial ───────────────────────────────────────────
st.markdown("""
<h1 style='text-align:center;
background: linear-gradient(135deg, #4158d0, #c850c0, #ffcc02);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
font-size: 3em;
font-weight: bold;'>
📱 Instagram & Bem-Estar
</h1>

<h3 style='text-align:center; color: #8888aa;'>
O Custo Psicológico das Redes Sociais
</h3>

<hr>
""", unsafe_allow_html=True)

st.markdown("""
<p style='text-align:center; color: #f0f0f5; font-size: 1.1em;'>
Laboratório de Análise de Dados — 2025/26
</p>
""", unsafe_allow_html=True)

# ── Cards de navegação ───────────────────────────────────────
st.markdown('## 🗺️ Escolhe o teu Dashboard')
st.markdown('<span style="color:#8888aa">Cada dashboard foi desenhado para um público específico.</span>', unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <a href="javascript:window.location.pathname='/investigador'" style="text-decoration: none; color: inherit;">
    <div style='background: linear-gradient(135deg, #111118, #1c1c28);
    border-radius: 15px; padding: 20px; border-left: 4px solid #c850c0;
    height: 200px;'>
    <h3 style='color: #c850c0;'>🔬 Investigador</h3>
    <p style='color: #f0f0f5;'>Análise técnica completa com correlações,
    distribuições e estatísticas avançadas. Filtros dinâmicos e exploração livre.</p>
    </div>
    </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <a href="javascript:window.location.pathname='/saude'" style="text-decoration: none; color: inherit;">
    <div style='background: linear-gradient(135deg, #111118, #1c1c28);
    border-radius: 15px; padding: 20px; border-left: 4px solid #ffcc02;
    height: 200px;'>
    <h3 style='color: #ffcc02;'>🧑‍⚕️ Profissional de Saúde</h3>
    <p style='color: #f0f0f5;'>Indicadores de risco, grupos vulneráveis e
    relação entre uso do Instagram e saúde mental.</p>
    </div>
    </a>
    """, unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    <a href="javascript:window.location.pathname='/utilizador'" style="text-decoration: none; color: inherit;">
    <div style='background: linear-gradient(135deg, #111118, #1c1c28);
    border-radius: 15px; padding: 20px; border-left: 4px solid #4158d0;
    height: 200px;'>
    <h3 style='color: #4158d0;'>📱 Utilizador Comum</h3>
    <p style='color: #f0f0f5;'>Define o teu perfil e compara-te com a média.
    Descobre a tua persona e nível de dependência digital.</p>
    </div>
    </a>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <a href="javascript:window.location.pathname='/marketing'" style="text-decoration: none; color: inherit;">
    <div style='background: linear-gradient(135deg, #111118, #1c1c28);
    border-radius: 15px; padding: 20px; border-left: 4px solid #c850c0;
    height: 200px;'>
    <h3 style='color: #c850c0;'>📊 Gestor de Marketing</h3>
    <p style='color: #f0f0f5;'>Personas, engagement, conteúdo preferido
    e comportamento por país. Insights para estratégia digital.</p>
    </div>
    </a>
    """, unsafe_allow_html=True)

st.divider()

st.markdown("""
<p style='text-align:center; color: #8888aa; font-size: 0.9em;'>
📊 Dataset: Social Media User Behavior & Lifestyle — 273.788 utilizadores sintéticos
| Kaggle CC0 Public Domain
</p>
""", unsafe_allow_html=True)