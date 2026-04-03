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

# CSS global
st.markdown("""
<style>
    .main { background-color: #0f0f0f; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f0f 100%);
    }
    .stMetric {
        background: linear-gradient(135deg, #1a1a2e, #2a2a4e);
        border-radius: 10px;
        padding: 10px;
        border-left: 3px solid #833ab4;
    }
    div[data-testid="stMetricValue"] { color: white; font-size: 1.4em; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa; }
</style>
""", unsafe_allow_html=True)

# ── Página inicial ───────────────────────────────────────────
st.markdown("""
<h1 style='text-align:center; background: linear-gradient(90deg, #833ab4, #fd1d1d, #fcb045);
-webkit-background-clip: text; -webkit-text-fill-color: transparent;
font-size: 3em; font-weight: bold;'>
📱 Instagram & Bem-Estar
</h1>
<h3 style='text-align:center; color: #aaaaaa;'>
O Custo Psicológico das Redes Sociais
</h3>
<hr style='border-color: #833ab4;'>
""", unsafe_allow_html=True)

st.markdown("""
<p style='text-align:center; color: #cccccc; font-size: 1.1em;'>
Laboratório de Análise de Dados — 2025/26
</p>
""", unsafe_allow_html=True)

# ── Cards de navegação ───────────────────────────────────────
st.markdown('## 🗺️ Escolhe o teu Dashboard')
st.markdown('Cada dashboard foi desenhado para um público específico.')
st.divider()

col1, col2, col3 = st.columns(3)
col4, col5 = st.columns(2)

with col1:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e, #2a2a4e);
    border-radius: 15px; padding: 20px; border-left: 4px solid #833ab4;
    height: 200px;'>
    <h3 style='color: #833ab4;'>🔬 Investigador</h3>
    <p style='color: #cccccc;'>Análise técnica completa com correlações,
    distribuições e estatísticas avançadas. Filtros dinâmicos e exploração livre.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e, #2a2a4e);
    border-radius: 15px; padding: 20px; border-left: 4px solid #fd1d1d;
    height: 200px;'>
    <h3 style='color: #fd1d1d;'>🧑‍⚕️ Profissional de Saúde</h3>
    <p style='color: #cccccc;'>Indicadores de risco, grupos vulneráveis e
    relação entre uso do Instagram e saúde mental.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e, #2a2a4e);
    border-radius: 15px; padding: 20px; border-left: 4px solid #fcb045;
    height: 200px;'>
    <h3 style='color: #fcb045;'>📱 Utilizador Comum</h3>
    <p style='color: #cccccc;'>Define o teu perfil e compara-te com a média.
    Descobre a tua persona e nível de dependência digital.</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e, #2a2a4e);
    border-radius: 15px; padding: 20px; border-left: 4px solid #405de6;
    height: 200px;'>
    <h3 style='color: #405de6;'>📊 Gestor de Marketing</h3>
    <p style='color: #cccccc;'>Personas, engagement, conteúdo preferido
    e comportamento por país. Insights para estratégia digital.</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e, #2a2a4e);
    border-radius: 15px; padding: 20px; border-left: 4px solid #e1306c;
    height: 200px;'>
    <h3 style='color: #e1306c;'>🏛️ Políticas Públicas</h3>
    <p style='color: #cccccc;'>Padrões populacionais de risco por país,
    faixa etária e género para campanhas de saúde digital.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.markdown("""
<p style='text-align:center; color: #666666; font-size: 0.9em;'>
📊 Dataset: Social Media User Behavior & Lifestyle — 273.788 utilizadores sintéticos
| Kaggle CC0 Public Domain
</p>
""", unsafe_allow_html=True)