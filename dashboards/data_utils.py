import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import streamlit as st
import os

# ── Paleta Neon Minimal ──────────────────────────────────────
NEON_GREEN  = '#00ff88'
NEON_PINK   = '#ff6bff'
NEON_YELLOW = '#ffdd00'
NEON_CYAN   = '#00ddff'
NEON_RED    = '#ff4466'
NEON_ORANGE = '#ff9944'
INSTA_COLORS = [NEON_GREEN, NEON_PINK, NEON_YELLOW, NEON_CYAN, NEON_RED, NEON_ORANGE, '#aa88ff']

BG_MAIN    = '#050508'
BG_CARD    = '#080810'
BG_SURFACE = '#0a0a14'
TEXT_DIM   = '#444466'
TEXT_MUTED = '#333355'

# Plotly layout base
PLOTLY_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Space Grotesk, sans-serif', color='rgba(255,255,255,0.85)', size=11),
    hoverlabel=dict(bgcolor='rgba(8,8,16,0.95)', font_size=12),
    margin=dict(t=50, b=40, l=40, r=20),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(255,255,255,0.1)', borderwidth=1),
)

def plotly_axes(fig, grid=True):
    gc = 'rgba(255,255,255,0.07)' if grid else 'rgba(0,0,0,0)'
    fig.update_xaxes(showgrid=False, linecolor='rgba(255,255,255,0.1)', linewidth=1, zeroline=False)
    fig.update_yaxes(gridcolor=gc, linecolor='rgba(255,255,255,0.1)', linewidth=1, zeroline=False)
    return fig

# ── Variáveis ────────────────────────────────────────────────
USAGE_VARS = [
    'daily_active_minutes_instagram', 'sessions_per_day',
    'reels_watched_per_day', 'stories_viewed_per_day',
    'time_on_feed_per_day', 'time_on_reels_per_day',
    'posts_created_per_week', 'likes_given_per_day',
    'average_session_length_minutes', 'user_engagement_score'
]

WELLBEING_VARS = [
    'perceived_stress_score', 'self_reported_happiness',
    'sleep_hours_per_night', 'exercise_hours_per_week',
    'daily_steps_count', 'body_mass_index',
    'blood_pressure_systolic', 'blood_pressure_diastolic'
]

PERSONAS = ['Doom-Scroller', 'Silent Browser', 'Utilizador Casual', 'Social Poster', 'Influencer/Creator']
PERSONA_COLORS = {p: c for p, c in zip(PERSONAS, INSTA_COLORS)}

# ── CSS Global Neon Minimal ──────────────────────────────────
def apply_neon_style(accent_color=NEON_GREEN):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        * {{ font-family: 'Space Grotesk', sans-serif; }}
        .stApp {{ background-color: {BG_MAIN}; }}
        [data-testid="stSidebar"] {{
            background: {BG_CARD};
            border-right: 1px solid {accent_color}22;
        }}
        .block-container {{ padding-top: 1.5rem; }}
        div[data-testid="stMetric"] {{
            background: {BG_SURFACE};
            border: 1px solid {accent_color}33;
            border-radius: 10px;
            padding: 14px;
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.6em !important;
            font-weight: 700 !important;
            color: {accent_color} !important;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {TEXT_DIM} !important;
            font-size: 0.75em !important;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        div[data-testid="stMetricDelta"] {{ font-size: 0.8em !important; }}
        h1, h2, h3 {{ color: #ffffff !important; }}
        div[role="tablist"] {{
            background: {BG_SURFACE} !important;
            border-radius: 10px !important;
            padding: 3px !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
        }}
        div[role="tablist"] button {{
            background: transparent !important;
            border: none !important;
            border-radius: 8px !important;
            color: {TEXT_DIM} !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.75em !important;
        }}
        div[role="tablist"] button[aria-selected="true"] {{
            background: {accent_color}11 !important;
            border: 1px solid {accent_color} !important;
            color: {accent_color} !important;
        }}
        div[data-testid="stSidebarContent"] label {{
            color: {TEXT_DIM} !important;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        [data-testid="stSidebarNav"] {{ display: none; }}
        .stAlert {{ border-radius: 10px !important; }}
        hr {{ border-color: rgba(255,255,255,0.06) !important; }}
    </style>
    """, unsafe_allow_html=True)

# ── Componentes UI ───────────────────────────────────────────
def page_header(emoji, titulo, subtitulo, historia, cor):
    st.html(f"""
    <div style='padding: 1.5rem 0 1rem 0; border-bottom: 1px solid {cor}33; margin-bottom: 1.5rem;'>
        <div style='display: flex; align-items: center; gap: 1rem;'>
            <div style='
                font-size: 2.5em;
                filter: drop-shadow(0 0 12px {cor});
            '>{emoji}</div>
            <div>
                <p style='color: {cor}; font-size: 0.7em; text-transform: uppercase;
                letter-spacing: 0.15em; font-weight: 700; margin: 0;'>{titulo}</p>
                <h1 style='color: #ffffff; margin: 0; font-size: 1.8em; font-weight: 700;
                letter-spacing: -0.02em;'>{subtitulo}</h1>
                <p style='color: #333355; font-size: 0.85em; font-style: italic; margin: 0;'>
                {historia}</p>
            </div>
        </div>
    </div>
    """)

def section_title(text, cor=NEON_GREEN):
    st.html(f"""
    <div style='
        display: flex; align-items: center; gap: 0.8rem;
        margin: 2rem 0 1rem 0;
    '>
        <div style='height: 1px; width: 20px; background: {cor};'></div>
        <p style='color: {cor}; font-size: 0.7em; text-transform: uppercase;
        letter-spacing: 0.15em; font-weight: 700; margin: 0;'>{text}</p>
        <div style='height: 1px; flex: 1; background: linear-gradient(90deg, {cor}44, transparent);'></div>
    </div>
    """)

def clinical_note(text, cor=NEON_GREEN):
    st.html(f"""
    <div style='
        background: {cor}08;
        border-left: 3px solid {cor};
        border-radius: 0 10px 10px 0;
        padding: 12px 16px;
        font-size: 0.82em;
        color: rgba(255,255,255,0.65);
        line-height: 1.6;
        margin: 0.5rem 0 1rem 0;
    '>💡 {text}</div>
    """)

def kpi_zone(label, value, sub, zone, col=None):
    colors = {'good': NEON_GREEN, 'mid': NEON_YELLOW, 'bad': NEON_RED}
    c = colors.get(zone, NEON_GREEN)
    html = f"""
    <div style='
        background: {BG_SURFACE};
        border: 1px solid {c}33;
        border-top: 2px solid {c};
        border-radius: 10px;
        padding: 16px;
    '>
        <p style='color: {TEXT_DIM}; font-size: 0.7em; text-transform: uppercase;
        letter-spacing: 0.1em; margin: 0 0 4px 0;'>{label}</p>
        <p style='color: {c}; font-size: 1.7em; font-weight: 700; margin: 0; line-height: 1;'>{value}</p>
        <p style='color: {TEXT_MUTED}; font-size: 0.72em; margin: 4px 0 0 0;'>{sub}</p>
    </div>
    """
    if col:
        col.html(html)
    else:
        st.html(html)

def pill_metric(label, value, ref='', tone=NEON_GREEN):
    st.html(f"""
    <div style='
        background: {BG_SURFACE};
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 14px 12px;
        text-align: center;
    '>
        <p style='color: {TEXT_DIM}; font-size: 0.68em; text-transform: uppercase;
        letter-spacing: 0.05em; margin: 0 0 3px 0;'>{label}</p>
        <p style='color: {tone}; font-size: 1.3em; font-weight: 700; margin: 0;'>{value}</p>
        <p style='color: {TEXT_MUTED}; font-size: 0.66em; margin: 2px 0 0 0;'>{ref}</p>
    </div>
    """)

def tip_card(text, good=False):
    cor = NEON_GREEN if good else NEON_YELLOW
    icon = '✅' if good else '⚠️'
    st.html(f"""
    <div style='
        background: {cor}08;
        border-left: 3px solid {cor};
        border-radius: 0 10px 10px 0;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.84em;
        color: rgba(255,255,255,0.75);
        line-height: 1.6;
    '>{icon} {text}</div>
    """)

# ── Carregamento ─────────────────────────────────────────────
def get_data_path():
    paths = [
        '../data/instagram_enriched.csv',
        'data/instagram_enriched.csv',
        os.path.join(os.path.dirname(__file__), '../data/instagram_enriched.csv'),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return '../data/instagram_enriched.csv'

@st.cache_data(ttl=3600, show_spinner='⏳ A carregar dados...')
def load_data(sample_size=100_000):
    path = get_data_path()
    try:
        df = pd.read_csv(path)
        if len(df) > sample_size:
            df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
        df = ensure_features(df)
        return df
    except FileNotFoundError:
        st.error(f'❌ Ficheiro não encontrado. Corre primeiro o notebook `06_new_variables.ipynb`')
        st.stop()

def ensure_features(df):
    scaler = MinMaxScaler()

    if 'digital_addiction_score' not in df.columns:
        cols = [c for c in ['daily_active_minutes_instagram', 'sessions_per_day', 'reels_watched_per_day'] if c in df.columns]
        if cols:
            scaled = scaler.fit_transform(df[cols].fillna(0))
            pesos = [0.5, 0.3, 0.2][:len(cols)]
            pesos = [p/sum(pesos) for p in pesos]
            df['digital_addiction_score'] = sum(scaled[:, i]*pesos[i] for i in range(len(cols))) * 100

    if 'wellbeing_index' not in df.columns:
        cols = [c for c in ['self_reported_happiness', 'sleep_hours_per_night', 'exercise_hours_per_week', 'perceived_stress_score'] if c in df.columns]
        if len(cols) >= 2:
            wb = df[cols].fillna(df[cols].median())
            scaled = scaler.fit_transform(wb)
            pesos = {'self_reported_happiness': 0.35, 'sleep_hours_per_night': 0.25, 'exercise_hours_per_week': 0.20, 'perceived_stress_score': 0.20}
            if 'perceived_stress_score' in cols:
                scaled[:, cols.index('perceived_stress_score')] = 1 - scaled[:, cols.index('perceived_stress_score')]
            df['wellbeing_index'] = sum(scaled[:, i]*pesos.get(col, 0.25) for i, col in enumerate(cols)) * 100

    if 'doom_scroll_ratio' not in df.columns:
        cols_p = [c for c in ['time_on_reels_per_day', 'time_on_feed_per_day'] if c in df.columns]
        if cols_p and 'daily_active_minutes_instagram' in df.columns:
            df['doom_scroll_ratio'] = (df[cols_p].sum(axis=1) / df['daily_active_minutes_instagram'].replace(0, np.nan)).clip(0, 1).fillna(0)

    if 'follower_ratio' not in df.columns:
        if all(c in df.columns for c in ['followers_count', 'following_count']):
            df['follower_ratio'] = (df['followers_count'] / (df['following_count'] + 1)).clip(0, 500)

    if 'user_persona' not in df.columns:
        def persona(row):
            a = row.get('digital_addiction_score', 50)
            r = row.get('follower_ratio', 1)
            p = row.get('posts_created_per_week', 0)
            if r > 10 or p > 5: return 'Influencer/Creator'
            elif a > 70:         return 'Doom-Scroller'
            elif a < 30:         return 'Utilizador Casual'
            elif p > 2:          return 'Social Poster'
            else:                return 'Silent Browser'
        df['user_persona'] = df.apply(persona, axis=1)

    if 'age_group' not in df.columns and 'age' in df.columns:
        df['age_group'] = pd.cut(df['age'], bins=[0,18,25,35,45,60,100],
                                  labels=['<18','18-25','26-35','36-45','46-60','60+']).astype(str)

    if 'screen_time_cat' not in df.columns and 'daily_active_minutes_instagram' in df.columns:
        df['screen_time_cat'] = pd.cut(df['daily_active_minutes_instagram'],
                                        bins=[0,30,60,120,240,9999],
                                        labels=['Mínimo','Baixo','Moderado','Alto','Excessivo']).astype(str)
    return df

def sidebar_filters(df, accent=NEON_GREEN, show_age=True, show_gender=True, show_persona=True, show_country=True, show_screen=True):
    filtered = df.copy()

    if show_age and 'age_group' in df.columns:
        opcoes = sorted(df['age_group'].dropna().unique().tolist())
        sel = st.sidebar.multiselect('Faixa Etária', opcoes, default=opcoes)
        if sel: filtered = filtered[filtered['age_group'].isin(sel)]

    if show_gender and 'gender' in df.columns:
        opcoes = sorted(df['gender'].dropna().unique().tolist())
        sel = st.sidebar.multiselect('Género', opcoes, default=opcoes)
        if sel: filtered = filtered[filtered['gender'].isin(sel)]

    if show_persona and 'user_persona' in df.columns:
        opcoes = df['user_persona'].dropna().unique().tolist()
        sel = st.sidebar.multiselect('Persona', opcoes, default=opcoes)
        if sel: filtered = filtered[filtered['user_persona'].isin(sel)]

    if show_country and 'country' in df.columns:
        opcoes = sorted(df['country'].dropna().unique().tolist())
        sel = st.sidebar.multiselect('País', opcoes, default=opcoes)
        if sel: filtered = filtered[filtered['country'].isin(sel)]

    if show_screen and 'daily_active_minutes_instagram' in df.columns:
        mn = int(df['daily_active_minutes_instagram'].min())
        mx = int(df['daily_active_minutes_instagram'].quantile(0.99))
        rng = st.sidebar.slider('Tempo Diário (min)', mn, mx, (mn, mx))
        filtered = filtered[filtered['daily_active_minutes_instagram'].between(*rng)]

    return filtered