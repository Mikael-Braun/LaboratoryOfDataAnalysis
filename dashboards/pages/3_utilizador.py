import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_utils import (load_data, apply_neon_style, page_header, section_title,
                        clinical_note, tip_card, pill_metric, kpi_zone,
                        PLOTLY_BASE, plotly_axes, INSTA_COLORS,
                        NEON_YELLOW, NEON_GREEN, NEON_RED, NEON_PINK, TEXT_DIM, BG_SURFACE)

st.set_page_config(page_title='O Meu Perfil', layout='wide', page_icon='📱')
apply_neon_style(NEON_YELLOW)

df = load_data(50_000)

page_header('📱', 'Dashboard — Utilizador Comum', 'O Meu Perfil Digital',
            '"Como te comparas com o mundo?"', NEON_YELLOW)

st.page_link('app.py', label='← 🏡', use_container_width=False)

# ── Formulário ────────────────────────────────────────────────
section_title('Define o Teu Perfil', NEON_YELLOW)
col1, col2, col3 = st.columns(3)

with col1:
    st.html(f"<p style='color:{NEON_YELLOW}; font-size:0.75em; text-transform:uppercase; letter-spacing:0.1em; font-weight:700;'>📱 Uso do Instagram</p>")
    user_minutos = st.slider('⏱️ Minutos por dia:', 0, 500, int(df['daily_active_minutes_instagram'].mean()))
    user_sessoes = st.slider('🔄 Sessões por dia:', 1, 50, int(df['sessions_per_day'].mean()))
    user_reels   = st.slider('🎬 Reels por dia:', 0, 300, int(df['reels_watched_per_day'].mean()))

with col2:
    st.html(f"<p style='color:{NEON_YELLOW}; font-size:0.75em; text-transform:uppercase; letter-spacing:0.1em; font-weight:700;'>💚 Bem-Estar</p>")
    user_stress     = st.slider('😰 Stress (0-40):', 0, 40, int(df['perceived_stress_score'].mean()))
    user_felicidade = st.slider('😊 Felicidade (1-10):', 1, 10, int(df['self_reported_happiness'].mean()))
    user_sono       = st.slider('😴 Horas de sono:', 3, 12, int(df['sleep_hours_per_night'].mean()))

with col3:
    st.html(f"<p style='color:{NEON_YELLOW}; font-size:0.75em; text-transform:uppercase; letter-spacing:0.1em; font-weight:700;'>🏃 Estilo de Vida</p>")
    user_exercicio = st.slider('🏋️ Exercício (h/semana):', 0, 20, int(df['exercise_hours_per_week'].mean()))
    user_idade     = st.slider('👤 Idade:', 13, 80, 28)
    user_genero    = st.selectbox('⚧️ Género:', sorted(df['gender'].dropna().unique().tolist()) if 'gender' in df.columns else ['Male','Female'])

st.divider()

# ── Cálculo das métricas ──────────────────────────────────────
def norm_val(val, col):
    mn, mx = df[col].min(), df[col].max()
    return np.clip((val - mn) / (mx - mn + 1e-9), 0, 1)

# Addiction score
maxs = df[['daily_active_minutes_instagram','sessions_per_day','reels_watched_per_day']].max().values
user_scaled = np.array([user_minutos/maxs[0], user_sessoes/maxs[1], user_reels/maxs[2]])
user_scaled = np.clip(user_scaled, 0, 1)
addiction_user = (user_scaled[0]*0.5 + user_scaled[1]*0.3 + user_scaled[2]*0.2) * 100

# Wellbeing index
stress_n   = 1 - norm_val(user_stress,    'perceived_stress_score')
felicid_n  = norm_val(user_felicidade,    'self_reported_happiness')
sono_n     = norm_val(user_sono,          'sleep_hours_per_night')
exercicio_n= norm_val(user_exercicio,     'exercise_hours_per_week')
wellbeing_user = (felicid_n*0.35 + sono_n*0.25 + exercicio_n*0.20 + stress_n*0.20) * 100

# Doom scroll ratio
doom_user = min((user_minutos * 0.6) / (user_minutos + 1), 1.0)

# Persona
def calc_persona(addiction, reels, sessoes):
    if addiction > 70: return 'Doom-Scroller', '😵', NEON_RED
    elif addiction < 30: return 'Utilizador Casual', '😌', NEON_GREEN
    elif sessoes > 15: return 'Social Poster', '📸', NEON_PINK
    else: return 'Silent Browser', '👁️', NEON_YELLOW

persona_user, emoji_persona, cor_persona = calc_persona(addiction_user, user_reels, user_sessoes)

# ── Resultados principais (com gauges — inspirado no patient.py) ─
section_title('Os Teus Resultados', NEON_YELLOW)

col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    # Gauge — Digital Addiction
    cor_add = NEON_RED if addiction_user > 70 else NEON_YELLOW if addiction_user > 40 else NEON_GREEN
    fig_gauge = go.Figure(go.Indicator(
        mode='gauge+number', value=round(addiction_user, 1),
        title={'text': 'Dependência Digital', 'font': {'size': 12, 'color': TEXT_DIM}},
        number={'font': {'size': 30, 'color': cor_add}, 'suffix': '/100'},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': TEXT_DIM, 'tickfont': {'size': 8}},
            'bar': {'color': cor_add, 'thickness': 0.22},
            'bgcolor': 'rgba(0,0,0,0)', 'borderwidth': 0,
            'steps': [
                {'range': [0, 30], 'color': 'rgba(0,255,136,0.1)'},
                {'range': [30, 70], 'color': 'rgba(255,221,0,0.1)'},
                {'range': [70, 100], 'color': 'rgba(255,68,102,0.1)'},
            ],
        }
    ))
    fig_gauge.update_layout(**{**PLOTLY_BASE, 'height': 220, 'margin': dict(l=20,r=20,t=40,b=10)})
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    # Gauge — Wellbeing
    cor_wb = NEON_GREEN if wellbeing_user > 60 else NEON_YELLOW if wellbeing_user > 40 else NEON_RED
    fig_wb = go.Figure(go.Indicator(
        mode='gauge+number', value=round(wellbeing_user, 1),
        title={'text': 'Wellbeing Index', 'font': {'size': 12, 'color': TEXT_DIM}},
        number={'font': {'size': 30, 'color': cor_wb}, 'suffix': '/100'},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': TEXT_DIM, 'tickfont': {'size': 8}},
            'bar': {'color': cor_wb, 'thickness': 0.22},
            'bgcolor': 'rgba(0,0,0,0)', 'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': 'rgba(255,68,102,0.1)'},
                {'range': [40, 60], 'color': 'rgba(255,221,0,0.1)'},
                {'range': [60, 100], 'color': 'rgba(0,255,136,0.1)'},
            ],
        }
    ))
    fig_wb.update_layout(**{**PLOTLY_BASE, 'height': 220, 'margin': dict(l=20,r=20,t=40,b=10)})
    st.plotly_chart(fig_wb, use_container_width=True)

with col3:
    # Persona card + métricas
    st.html(f"""
    <div style='
        background: {cor_persona}11;
        border: 1px solid {cor_persona}44;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    '>
        <div style='font-size: 2.5em; margin-bottom: 0.3rem;'>{emoji_persona}</div>
        <p style='color: {cor_persona}; font-size: 0.7em; text-transform: uppercase;
        letter-spacing: 0.15em; font-weight: 700; margin: 0;'>A tua persona</p>
        <h2 style='color: #ffffff; margin: 0.2rem 0; font-size: 1.4em;'>{persona_user}</h2>
        <p style='color: #333355; font-size: 0.8em; margin: 0;'>
            Baseado no teu padrão de uso
        </p>
    </div>
    """)

st.html("<br>")
# Pills com métricas (inspirado no patient.py)
c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: pill_metric('⏱️ Tempo/Dia', f'{user_minutos} min', f'Média: {df["daily_active_minutes_instagram"].mean():.0f}', NEON_YELLOW if user_minutos > df['daily_active_minutes_instagram'].mean() else NEON_GREEN)
with c2: pill_metric('😰 Stress', f'{user_stress}/40', f'Média: {df["perceived_stress_score"].mean():.1f}', NEON_RED if user_stress > 25 else NEON_YELLOW if user_stress > 15 else NEON_GREEN)
with c3: pill_metric('😊 Felicidade', f'{user_felicidade}/10', f'Média: {df["self_reported_happiness"].mean():.1f}', NEON_GREEN if user_felicidade >= 7 else NEON_YELLOW)
with c4: pill_metric('😴 Sono', f'{user_sono}h', 'OMS: 7-9h', NEON_GREEN if 7 <= user_sono <= 9 else NEON_RED)
with c5: pill_metric('🏋️ Exercício', f'{user_exercicio}h/sem', 'OMS: 2.5h/sem', NEON_GREEN if user_exercicio >= 2.5 else NEON_YELLOW)
with c6: pill_metric('🎬 Reels/Dia', f'{user_reels}', f'Média: {df["reels_watched_per_day"].mean():.0f}', NEON_RED if user_reels > 150 else NEON_YELLOW)

st.divider()

# ── Radar Chart — Tu vs Média ────────────────────────────────
section_title('O Teu Perfil vs a Média', NEON_YELLOW)
col1, col2 = st.columns([3, 2])

with col1:
    radar_labels = ['Dependência\nDigital','Bem-Estar','Stress\n(inv.)','Felicidade','Sono','Exercício']
    user_radar = [
        addiction_user/100, wellbeing_user/100,
        1-norm_val(user_stress,'perceived_stress_score'),
        norm_val(user_felicidade,'self_reported_happiness'),
        norm_val(user_sono,'sleep_hours_per_night'),
        norm_val(user_exercicio,'exercise_hours_per_week'),
    ]
    media_radar = [
        df['digital_addiction_score'].mean()/100,
        df['wellbeing_index'].mean()/100,
        1-norm_val(df['perceived_stress_score'].mean(),'perceived_stress_score'),
        norm_val(df['self_reported_happiness'].mean(),'self_reported_happiness'),
        norm_val(df['sleep_hours_per_night'].mean(),'sleep_hours_per_night'),
        norm_val(df['exercise_hours_per_week'].mean(),'exercise_hours_per_week'),
    ]

    def hex_to_rgba(hex_color, alpha=0.15):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f'rgba({r},{g},{b},{alpha})'

    fig_radar = go.Figure()
    for valores, nome, cor in [(user_radar,'Tu',NEON_YELLOW),(media_radar,'Média Geral',NEON_GREEN)]:
        v = valores + [valores[0]]
        l = radar_labels + [radar_labels[0]]
        fig_radar.add_trace(go.Scatterpolar(
            r=v, theta=l, fill='toself', name=nome,
            line_color=cor, fillcolor=hex_to_rgba(cor, alpha=0.15),
            opacity=0.8
        ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,1], tickfont=dict(size=8), gridcolor='rgba(255,255,255,0.1)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True, height=400, **PLOTLY_BASE
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col2:
    # Tu vs Média — barra comparativa
    section_title('Tu vs Média da População', NEON_YELLOW)
    comparacao = [
        ('Minutos/Dia', user_minutos, df['daily_active_minutes_instagram'].mean()),
        ('Stress', user_stress, df['perceived_stress_score'].mean()),
        ('Felicidade', user_felicidade, df['self_reported_happiness'].mean()),
        ('Sono (h)', user_sono, df['sleep_hours_per_night'].mean()),
        ('Exercício (h)', user_exercicio, df['exercise_hours_per_week'].mean()),
    ]
    fig_comp = go.Figure()
    y_labels = [c[0] for c in comparacao]
    user_vals = [c[1] for c in comparacao]
    media_vals = [c[2] for c in comparacao]

    fig_comp.add_trace(go.Bar(name='Tu', y=y_labels, x=user_vals, orientation='h',
                              marker_color=NEON_YELLOW, opacity=0.8))
    fig_comp.add_trace(go.Bar(name='Média', y=y_labels, x=media_vals, orientation='h',
                              marker_color='rgba(255,255,255,0.2)', opacity=0.8))
    fig_comp.update_layout(**{**PLOTLY_BASE, 'barmode': 'overlay', 'height': 350, 
                          'margin': dict(l=100,r=20,t=30,b=20)})
    plotly_axes(fig_comp)
    st.plotly_chart(fig_comp, use_container_width=True)

st.divider()

# ── Recomendações personalizadas (inspirado no patient.py) ────
section_title('Recomendações Personalizadas', NEON_YELLOW)

tips = []
if user_minutos > 240:
    tips.append((f'Usas {user_minutos} min/dia — mais de 4h. A APA considera >2h potencialmente prejudicial. '
                  f'A média é {df["daily_active_minutes_instagram"].mean():.0f} min.', False))
elif user_minutos <= 60:
    tips.append(('Excelente! O teu tempo de uso está abaixo de 1h/dia — muito saudável.', True))

if user_stress > 25:
    tips.append((f'Stress elevado ({user_stress}/40). Utilizadores com este nível de stress '
                  f'usam em média 160 minutos a mais no Instagram por dia.', False))
elif user_stress <= 10:
    tips.append(('Nível de stress muito baixo — excelente indicador de bem-estar!', True))

if user_sono < 6:
    tips.append(f'Dormes apenas {user_sono}h/noite. A OMS recomenda 7-9h. '
                 f'A privação de sono aumenta significativamente a resistência à insulina e o stress.' , False)
elif 7 <= user_sono <= 9:
    tips.append(('Horas de sono ideais! Manter 7-9h por noite é um dos melhores investimentos na saúde.', True))

if user_reels > 150:
    tips.append((f'Vês {user_reels} Reels por dia — muito acima da média '
                  f'({df["reels_watched_per_day"].mean():.0f}). O consumo passivo de conteúdo '
                  f'está associado a maior stress (r=0.68 neste dataset).', False))

if user_exercicio >= 5:
    tips.append(('Ótima actividade física! O exercício regular é um factor protector contra o stress.', True))
elif user_exercicio < 2.5:
    tips.append((f'Apenas {user_exercicio}h de exercício por semana. '
                  f'A OMS recomenda pelo menos 2.5h de actividade moderada semanal.', False))

if persona_user == 'Doom-Scroller':
    tips.append(('O teu perfil é de Doom-Scroller — uso intenso e passivo. '
                  'Considera definir limites diários e substituir Reels por conteúdo activo.', False))
elif persona_user == 'Utilizador Casual':
    tips.append(('Perfil de Utilizador Casual — uso saudável e equilibrado. Continua assim!', True))

tips = sorted(tips, key=lambda x: x[1] if isinstance(x, tuple) else False)[:6]
for tip in tips:
    if isinstance(tip, tuple):
        tip_card(tip[0], good=tip[1])
    else:
        tip_card(tip, good=False)

clinical_note('Este relatório é indicativo e baseado em dados sintéticos. '
              'Não substitui aconselhamento médico ou psicológico profissional.', NEON_YELLOW)

st.html(f"<p style='color:#1a1a2e; font-size:0.8em; text-align:center; margin-top:3rem;'>📱 Dashboard Utilizador · LAD 2025/26</p>")