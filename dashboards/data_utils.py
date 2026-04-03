# ============================================================
# DATA UTILS — Funções partilhadas por todos os dashboards
# ============================================================
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import streamlit as st
import os

# ── Constantes globais ───────────────────────────────────────
INSTA_COLORS = [
    '#833ab4','#fd1d1d','#fcb045',
    '#405de6','#5851db','#e1306c','#f77737'
]

INSTA_GRADIENT = ['#833ab4', '#c13584', '#e1306c', '#fd1d1d', '#f77737', '#fcb045']

PERSONAS = [
    'Doom-Scroller', 'Silent Browser',
    'Utilizador Casual', 'Social Poster', 'Influencer/Creator'
]

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
    'daily_steps_count', 'body_mass_index'
]

DEMOGRAPHIC_VARS = [
    'age', 'gender', 'country', 'income_level',
    'education_level', 'employment_status',
    'urban_rural', 'relationship_status'
]

# ── Caminho do dataset ───────────────────────────────────────
def get_data_path():
    # Tenta caminhos relativos comuns
    paths = [
        '../data/instagram_enriched.csv',
        'data/instagram_enriched.csv',
        os.path.join(os.path.dirname(__file__), '../data/instagram_enriched.csv'),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return '../data/instagram_enriched.csv'

# ── Carregamento com cache ───────────────────────────────────
@st.cache_data(ttl=3600, show_spinner='⏳ A carregar dados...')
def load_data(sample_size=100_000):
    path = get_data_path()
    try:
        df = pd.read_csv(path)
        if len(df) > sample_size:
            df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)

        # Garante que as features existem
        df = ensure_features(df)
        return df

    except FileNotFoundError:
        st.error(f'❌ Ficheiro não encontrado: `{path}`')
        st.info('💡 Corre primeiro o notebook `06_new_variables.ipynb`')
        st.stop()

# ── Garante que todas as features existem ───────────────────
def ensure_features(df):
    scaler = MinMaxScaler()

    # Digital Addiction Score
    if 'digital_addiction_score' not in df.columns:
        cols = [c for c in ['daily_active_minutes_instagram',
                            'sessions_per_day', 'reels_watched_per_day']
                if c in df.columns]
        if cols:
            scaled = scaler.fit_transform(df[cols].fillna(0))
            pesos  = [0.5, 0.3, 0.2][:len(cols)]
            pesos  = [p/sum(pesos) for p in pesos]
            df['digital_addiction_score'] = sum(
                scaled[:, i] * pesos[i] for i in range(len(cols))
            ) * 100

    # Wellbeing Index
    if 'wellbeing_index' not in df.columns:
        cols = [c for c in ['self_reported_happiness', 'sleep_hours_per_night',
                            'exercise_hours_per_week', 'perceived_stress_score']
                if c in df.columns]
        if len(cols) >= 2:
            wb      = df[cols].fillna(df[cols].median())
            scaled  = scaler.fit_transform(wb)
            pesos   = {'self_reported_happiness': 0.35,
                      'sleep_hours_per_night': 0.25,
                      'exercise_hours_per_week': 0.20,
                      'perceived_stress_score': 0.20}
            if 'perceived_stress_score' in cols:
                idx = cols.index('perceived_stress_score')
                scaled[:, idx] = 1 - scaled[:, idx]
            df['wellbeing_index'] = sum(
                scaled[:, i] * pesos.get(col, 0.25)
                for i, col in enumerate(cols)
            ) * 100

    # Doom Scroll Ratio
    if 'doom_scroll_ratio' not in df.columns:
        cols_p = [c for c in ['time_on_reels_per_day', 'time_on_feed_per_day']
                  if c in df.columns]
        if cols_p and 'daily_active_minutes_instagram' in df.columns:
            passive = df[cols_p].sum(axis=1)
            total   = df['daily_active_minutes_instagram'].replace(0, np.nan)
            df['doom_scroll_ratio'] = (passive / total).clip(0, 1).fillna(0)

    # Follower Ratio
    if 'follower_ratio' not in df.columns:
        if all(c in df.columns for c in ['followers_count', 'following_count']):
            df['follower_ratio'] = (
                df['followers_count'] / (df['following_count'] + 1)
            ).clip(0, 500)

    # User Persona
    if 'user_persona' not in df.columns:
        def persona(row):
            a = row.get('digital_addiction_score', 50)
            r = row.get('follower_ratio', 1)
            p = row.get('posts_created_per_week', 0)
            if r > 10 or p > 5:  return 'Influencer/Creator'
            elif a > 70:          return 'Doom-Scroller'
            elif a < 30:          return 'Utilizador Casual'
            elif p > 2:           return 'Social Poster'
            else:                 return 'Silent Browser'
        df['user_persona'] = df.apply(persona, axis=1)

    # Age Group
    if 'age_group' not in df.columns and 'age' in df.columns:
        df['age_group'] = pd.cut(
            df['age'],
            bins=[0, 18, 25, 35, 45, 60, 100],
            labels=['<18', '18-25', '26-35', '36-45', '46-60', '60+']
        ).astype(str)

    # Screen Time Category
    if 'screen_time_cat' not in df.columns and 'daily_active_minutes_instagram' in df.columns:
        df['screen_time_cat'] = pd.cut(
            df['daily_active_minutes_instagram'],
            bins=[0, 30, 60, 120, 240, 9999],
            labels=['Mínimo (<30min)', 'Baixo (30-60min)',
                    'Moderado (1-2h)', 'Alto (2-4h)', 'Excessivo (>4h)']
        ).astype(str)

    return df

# ── Filtros sidebar genéricos ────────────────────────────────
def sidebar_filters(df, show_age=True, show_gender=True,
                    show_persona=True, show_country=True,
                    show_screen_time=True):
    st.sidebar.header('🔍 Filtros')
    filtered = df.copy()

    if show_age and 'age_group' in df.columns:
        opcoes = sorted(df['age_group'].dropna().unique().tolist())
        sel = st.sidebar.multiselect('Faixa Etária', opcoes, default=opcoes)
        if sel:
            filtered = filtered[filtered['age_group'].isin(sel)]

    if show_gender and 'gender' in df.columns:
        opcoes = sorted(df['gender'].dropna().unique().tolist())
        sel = st.sidebar.multiselect('Género', opcoes, default=opcoes)
        if sel:
            filtered = filtered[filtered['gender'].isin(sel)]

    if show_persona and 'user_persona' in df.columns:
        opcoes = df['user_persona'].dropna().unique().tolist()
        sel = st.sidebar.multiselect('Persona', opcoes, default=opcoes)
        if sel:
            filtered = filtered[filtered['user_persona'].isin(sel)]

    if show_country and 'country' in df.columns:
        opcoes = sorted(df['country'].dropna().unique().tolist())
        sel = st.sidebar.multiselect('País', opcoes, default=opcoes)
        if sel:
            filtered = filtered[filtered['country'].isin(sel)]

    if show_screen_time and 'daily_active_minutes_instagram' in df.columns:
        min_val = int(df['daily_active_minutes_instagram'].min())
        max_val = int(df['daily_active_minutes_instagram'].quantile(0.99))
        rng = st.sidebar.slider(
            'Tempo Diário (min)',
            min_val, max_val, (min_val, max_val)
        )
        filtered = filtered[
            filtered['daily_active_minutes_instagram'].between(*rng)
        ]

    return filtered

# ── KPIs ────────────────────────────────────────────────────
def render_kpis(df):
    kpis = [
        ('⏱️ Tempo Médio/Dia',   'daily_active_minutes_instagram', '{:.0f} min'),
        ('😰 Stress Médio',      'perceived_stress_score',         '{:.1f}'),
        ('😊 Felicidade',        'self_reported_happiness',        '{:.2f}'),
        ('💚 Wellbeing Index',   'wellbeing_index',                '{:.1f}/100'),
        ('🎯 Addiction Score',   'digital_addiction_score',        '{:.1f}/100'),
    ]
    cols = st.columns(len(kpis))
    for col, (label, key, fmt) in zip(cols, kpis):
        if key in df.columns:
            val = df[key].mean()
            col.metric(label, fmt.format(val))

# ── Estilo CSS global ────────────────────────────────────────
def apply_style():
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
        h1, h2, h3 { color: white; }
        .instagram-badge {
            background: linear-gradient(45deg, #833ab4, #fd1d1d, #fcb045);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
            font-size: 1.2em;
        }
    </style>
    """, unsafe_allow_html=True)