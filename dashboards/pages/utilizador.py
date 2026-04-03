# ============================================================
# DASHBOARD 3 — UTILIZADOR COMUM
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_utils import load_data, apply_style, INSTA_COLORS

st.set_page_config(page_title='📱 O Meu Perfil', layout='wide', page_icon='📱')
apply_style()

st.title('📱 Dashboard — O Meu Perfil Digital')
st.markdown('*Define o teu perfil e compara-te com a média dos utilizadores*')
st.divider()

df = load_data(50_000)

# ── Formulário do utilizador ─────────────────────────────────
st.markdown('## 👤 Define o teu perfil')
st.markdown('Preenche os campos abaixo para descobrires a tua persona digital.')

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('**📱 Uso do Instagram**')
    user_minutos = st.slider(
        '⏱️ Minutos por dia no Instagram:', 0, 500,
        int(df['daily_active_minutes_instagram'].mean())
    )
    user_sessoes = st.slider(
        '🔄 Sessões por dia:', 1, 50,
        int(df['sessions_per_day'].mean())
    )
    user_reels = st.slider(
        '🎬 Reels vistos por dia:', 0, 300,
        int(df['reels_watched_per_day'].mean())
    )

with col2:
    st.markdown('**💚 Bem-Estar**')
    user_stress = st.slider(
        '😰 Nível de stress (0-40):', 0, 40,
        int(df['perceived_stress_score'].mean())
    )
    user_felicidade = st.slider(
        '😊 Felicidade (1-10):', 1, 10,
        int(df['self_reported_happiness'].mean())
    )
    user_sono = st.slider(
        '😴 Horas de sono por noite:', 3, 12,
        int(df['sleep_hours_per_night'].mean())
    )

with col3:
    st.markdown('**🏃 Estilo de Vida**')
    user_exercicio = st.slider(
        '🏋️ Horas de exercício/semana:', 0, 20,
        int(df['exercise_hours_per_week'].mean())
    )
    user_idade = st.slider('👤 Idade:', 13, 80, 28)
    user_genero = st.selectbox(
        '⚧️ Género:',
        df['gender'].dropna().unique().tolist()
        if 'gender' in df.columns else ['Male', 'Female']
    )

st.divider()

# ── Cálculo das métricas do utilizador ──────────────────────
from sklearn.preprocessing import MinMaxScaler

def calcular_addiction(minutos, sessoes, reels, df):
    scaler = MinMaxScaler()
    cols   = ['daily_active_minutes_instagram', 'sessions_per_day', 'reels_watched_per_day']
    scaled = scaler.fit_transform(df[cols].fillna(0))
    maxs   = df[cols].max().values
    user_s = np.array([minutos/maxs[0], sessoes/maxs[1], reels/maxs[2]])
    user_s = np.clip(user_s, 0, 1)
    return (user_s[0]*0.5 + user_s[1]*0.3 + user_s[2]*0.2) * 100

def calcular_wellbeing(stress, felicidade, sono, exercicio, df):
    cols = ['perceived_stress_score', 'self_reported_happiness',
            'sleep_hours_per_night', 'exercise_hours_per_week']
    scaler  = MinMaxScaler()
    scaled  = scaler.fit_transform(df[cols].fillna(df[cols].median()))
    maxs    = df[cols].max().values
    mins    = df[cols].min().values
    def norm(val, mn, mx): return np.clip((val-mn)/(mx-mn+1e-9), 0, 1)
    stress_n   = 1 - norm(stress,    mins[0], maxs[0])
    felicid_n  = norm(felicidade,    mins[1], maxs[1])
    sono_n     = norm(sono,          mins[2], maxs[2])
    exercicio_n= norm(exercicio,     mins[3], maxs[3])
    return (felicid_n*0.35 + sono_n*0.25 + exercicio_n*0.20 + stress_n*0.20) * 100

def calcular_persona(addiction, reels, sessoes):
    if addiction > 70:    return 'Doom-Scroller', '😵'
    elif addiction < 30:  return 'Utilizador Casual', '😌'
    elif sessoes > 15:    return 'Social Poster', '📸'
    else:                 return 'Silent Browser', '👁️'

addiction_user  = calcular_addiction(user_minutos, user_sessoes, user_reels, df)
wellbeing_user  = calcular_wellbeing(user_stress, user_felicidade, user_sono, user_exercicio, df)
persona_user, emoji_persona = calcular_persona(addiction_user, user_reels, user_sessoes)

# Médias da população filtrada por género e idade próxima
faixa = pd.cut([user_idade],
               bins=[0,18,25,35,45,60,100],
               labels=['<18','18-25','26-35','36-45','46-60','60+'])[0]
df_comp = df[df['gender'] == user_genero] if 'gender' in df.columns else df

# ── Resultados ───────────────────────────────────────────────
st.markdown('## 📊 Os teus resultados')

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    '🎯 Dependência Digital',
    f'{addiction_user:.1f}/100',
    delta=f'{addiction_user - df["digital_addiction_score"].mean():.1f} vs média'
)
col2.metric(
    '💚 Bem-Estar',
    f'{wellbeing_user:.1f}/100',
    delta=f'{wellbeing_user - df["wellbeing_index"].mean():.1f} vs média'
)
col3.metric(
    '👥 Tua Persona',
    f'{emoji_persona} {persona_user}'
)
col4.metric(
    '⏱️ Tempo/Dia',
    f'{user_minutos} min',
    delta=f'{user_minutos - df["daily_active_minutes_instagram"].mean():.0f} vs média'
)

st.divider()

# ── Radar Chart — Tu vs Média ────────────────────────────────
st.markdown('## 🕸️ O teu perfil vs a média')

radar_labels = [
    'Dependência Digital', 'Bem-Estar',
    'Stress (inv.)', 'Felicidade', 'Sono', 'Exercício'
]

# Normaliza para [0,1]
def norm_val(val, col):
    mn = df[col].min()
    mx = df[col].max()
    return np.clip((val - mn) / (mx - mn + 1e-9), 0, 1)

user_radar = [
    addiction_user / 100,
    wellbeing_user / 100,
    1 - norm_val(user_stress,    'perceived_stress_score'),
    norm_val(user_felicidade,    'self_reported_happiness'),
    norm_val(user_sono,          'sleep_hours_per_night'),
    norm_val(user_exercicio,     'exercise_hours_per_week'),
]

media_radar = [
    df['digital_addiction_score'].mean() / 100,
    df['wellbeing_index'].mean() / 100,
    1 - norm_val(df['perceived_stress_score'].mean(), 'perceived_stress_score'),
    norm_val(df['self_reported_happiness'].mean(),    'self_reported_happiness'),
    norm_val(df['sleep_hours_per_night'].mean(),      'sleep_hours_per_night'),
    norm_val(df['exercise_hours_per_week'].mean(),    'exercise_hours_per_week'),
]

fig_radar = go.Figure()

for valores, nome, cor in [
    (user_radar,  'Tu',    '#fd1d1d'),
    (media_radar, 'Média', '#833ab4'),
]:
    v = valores + [valores[0]]
    l = radar_labels + [radar_labels[0]]
    fig_radar.add_trace(go.Scatterpolar(
        r=v, theta=l,
        fill='toself', name=nome,
        line_color=cor, opacity=0.7
    ))

fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    title=f'O teu perfil vs a média ({user_genero})',
    template='plotly_dark',
    paper_bgcolor='#0f0f0f',
    height=500
)
st.plotly_chart(fig_radar, use_container_width=True)

# ── Mensagem personalizada ───────────────────────────────────
st.divider()
st.markdown('## 💬 O que isto significa para ti')

col1, col2 = st.columns(2)

with col1:
    st.markdown('**📱 O teu uso do Instagram:**')
    if user_minutos > 240:
        st.error(f'⚠️ Usas **{user_minutos} min/dia** — acima de 4h. '
                 f'A média é {df["daily_active_minutes_instagram"].mean():.0f} min/dia.')
    elif user_minutos > 120:
        st.warning(f'🟡 Usas **{user_minutos} min/dia** — uso moderado-alto. '
                   f'A média é {df["daily_active_minutes_instagram"].mean():.0f} min/dia.')
    else:
        st.success(f'✅ Usas **{user_minutos} min/dia** — uso saudável! '
                   f'A média é {df["daily_active_minutes_instagram"].mean():.0f} min/dia.')

    st.markdown('**😰 O teu stress:**')
    if user_stress > 25:
        st.error(f'⚠️ Stress elevado ({user_stress}/40). '
                 f'A média é {df["perceived_stress_score"].mean():.1f}/40.')
    elif user_stress > 15:
        st.warning(f'🟡 Stress moderado ({user_stress}/40).')
    else:
        st.success(f'✅ Stress baixo ({user_stress}/40).')

with col2:
    st.markdown('**😴 O teu sono:**')
    if user_sono < 6:
        st.error(f'⚠️ Dormes apenas **{user_sono}h/noite**. '
                 f'A OMS recomenda 7-9h.')
    elif user_sono < 7:
        st.warning(f'🟡 Dormes **{user_sono}h/noite** — abaixo do ideal.')
    else:
        st.success(f'✅ Dormes **{user_sono}h/noite** — ótimo!')

    st.markdown('**💚 O teu bem-estar geral:**')
    if wellbeing_user < 40:
        st.error(f'⚠️ Wellbeing Index: **{wellbeing_user:.1f}/100** — baixo.')
    elif wellbeing_user < 60:
        st.warning(f'🟡 Wellbeing Index: **{wellbeing_user:.1f}/100** — moderado.')
    else:
        st.success(f'✅ Wellbeing Index: **{wellbeing_user:.1f}/100** — bom!')

# Dica personalizada
st.divider()
st.markdown('### 💡 Dica personalizada')
if addiction_user > 70 and user_stress > 20:
    st.markdown("""
    > 🔴 **Alto risco detectado.** O teu perfil combina uso intenso do Instagram
    com níveis elevados de stress. A literatura científica sugere que reduzir
    o tempo de ecrã, especialmente o consumo de Reels, pode ter um impacto
    positivo no bem-estar. Considera definir limites diários de uso.
    """)
elif user_sono < 6 and user_minutos > 120:
    st.markdown("""
    > 🟡 **Atenção ao sono.** Usar o Instagram antes de dormir está associado
    a menor qualidade do sono. Tenta não usar o telemóvel na última hora
    antes de adormecer.
    """)
else:
    st.markdown("""
    > 🟢 **Bom equilíbrio!** O teu uso das redes sociais parece estar dentro
    de limites saudáveis. Mantém os bons hábitos de sono e exercício.
    """)