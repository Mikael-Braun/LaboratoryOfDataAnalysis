# ============================================================
# DASHBOARD 1 — INVESTIGADOR / ANALISTA DE DADOS
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_utils import (load_data, sidebar_filters, render_kpis,
                        apply_style, INSTA_COLORS, USAGE_VARS, WELLBEING_VARS)

st.set_page_config(page_title='🔬 Investigador', layout='wide',
                   page_icon='🔬')
apply_style()

st.title('🔬 Dashboard — Investigador / Analista de Dados')
st.markdown('*Exploração técnica completa do dataset*')
st.divider()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header('⚙️ Configuração')
    sample = st.select_slider(
        'Tamanho da Amostra',
        options=[10_000, 25_000, 50_000, 100_000],
        value=50_000
    )
    st.divider()

df = load_data(sample)
df = sidebar_filters(df)

st.info(f'📊 A analisar **{len(df):,} utilizadores** com os filtros actuais')

# ── KPIs ─────────────────────────────────────────────────────
render_kpis(df)
st.divider()

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    '📊 Distribuições',
    '🔗 Correlações',
    '📐 Estatísticas',
    '🔍 Explorador',
    '📈 Assimetria'
])

# ── Tab 1: Distribuições ─────────────────────────────────────
with tab1:
    st.subheader('📊 Distribuições das Variáveis Principais')

    col1, col2 = st.columns(2)
    with col1:
        var_dist = st.selectbox(
            'Seleciona variável:',
            options=[v for v in USAGE_VARS + WELLBEING_VARS if v in df.columns]
        )
    with col2:
        n_bins = st.slider('Nº de bins:', 20, 100, 50)

    fig = px.histogram(
        df, x=var_dist, nbins=n_bins,
        color_discrete_sequence=[INSTA_COLORS[0]],
        title=f'Distribuição de {var_dist.replace("_"," ").title()}',
        template='plotly_dark', marginal='box'
    )
    fig.add_vline(x=df[var_dist].mean(), line_dash='dash',
                  line_color='white',
                  annotation_text=f'Média: {df[var_dist].mean():.2f}')
    fig.add_vline(x=df[var_dist].median(), line_dash='dot',
                  line_color='yellow',
                  annotation_text=f'Mediana: {df[var_dist].median():.2f}')
    fig.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e')
    st.plotly_chart(fig, use_container_width=True)

    # Estatísticas rápidas
    s = df[var_dist].dropna()
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric('Média',    f'{s.mean():.3f}')
    c2.metric('Mediana',  f'{s.median():.3f}')
    c3.metric('D.P.',     f'{s.std():.3f}')
    c4.metric('Mínimo',   f'{s.min():.3f}')
    c5.metric('Máximo',   f'{s.max():.3f}')
    c6.metric('IQR',      f'{s.quantile(0.75)-s.quantile(0.25):.3f}')

# ── Tab 2: Correlações ───────────────────────────────────────
with tab2:
    st.subheader('🔗 Mapa de Correlações')

    num_cols = df.select_dtypes(include='number').columns.tolist()
    default_cols = [c for c in
        ['daily_active_minutes_instagram', 'perceived_stress_score',
         'self_reported_happiness', 'sleep_hours_per_night',
         'wellbeing_index', 'digital_addiction_score',
         'reels_watched_per_day', 'exercise_hours_per_week']
        if c in num_cols]

    sel_cols = st.multiselect(
        'Seleciona variáveis:', options=num_cols, default=default_cols
    )

    if len(sel_cols) >= 2:
        metodo = st.radio(
            'Método:', ['pearson', 'spearman'], horizontal=True
        )
        corr = df[sel_cols].corr(method=metodo)
        fig_heat = px.imshow(
            corr, text_auto='.2f',
            color_continuous_scale='RdBu_r',
            title=f'Correlações de {metodo.title()}',
            template='plotly_dark',
            zmin=-1, zmax=1, aspect='auto'
        )
        fig_heat.update_layout(paper_bgcolor='#0f0f0f', height=600)
        st.plotly_chart(fig_heat, use_container_width=True)

        # Top correlações
        pairs = (
            corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
            .stack().reset_index()
        )
        pairs.columns = ['Var A', 'Var B', 'r']
        pairs['|r|'] = pairs['r'].abs()
        pairs = pairs.sort_values('|r|', ascending=False)

        st.markdown('**🔝 Top 10 correlações mais fortes:**')
        st.dataframe(
            pairs.head(10)[['Var A', 'Var B', 'r']].round(4),
            use_container_width=True
        )

# ── Tab 3: Estatísticas ──────────────────────────────────────
with tab3:
    st.subheader('📐 Estatísticas Descritivas Completas')

    grupo = st.radio(
        'Grupo de variáveis:',
        ['Uso do Instagram', 'Bem-Estar', 'Todas'],
        horizontal=True
    )

    if grupo == 'Uso do Instagram':
        vars_sel = [v for v in USAGE_VARS if v in df.columns]
    elif grupo == 'Bem-Estar':
        vars_sel = [v for v in WELLBEING_VARS if v in df.columns]
    else:
        vars_sel = [v for v in USAGE_VARS + WELLBEING_VARS if v in df.columns]

    from scipy.stats import skew, kurtosis
    stats_rows = []
    for col in vars_sel:
        s = df[col].dropna()
        stats_rows.append({
            'Variável':      col,
            'Média':         round(s.mean(), 3),
            'Mediana':       round(s.median(), 3),
            'D.P.':          round(s.std(), 3),
            'Variância':     round(s.var(), 3),
            'Mínimo':        round(s.min(), 3),
            'Máximo':        round(s.max(), 3),
            'Q1':            round(s.quantile(0.25), 3),
            'Q3':            round(s.quantile(0.75), 3),
            'IQR':           round(s.quantile(0.75)-s.quantile(0.25), 3),
            'Assimetria':    round(skew(s), 3),
            'Curtose':       round(kurtosis(s), 3),
        })

    st.dataframe(
        pd.DataFrame(stats_rows).set_index('Variável'),
        use_container_width=True
    )

# ── Tab 4: Explorador ────────────────────────────────────────
with tab4:
    st.subheader('🔍 Explorador de Variáveis')

    col1, col2, col3 = st.columns(3)
    num_vars = df.select_dtypes(include='number').columns.tolist()

    with col1:
        x_var = st.selectbox('Eixo X:', num_vars,
                             index=num_vars.index('digital_addiction_score')
                             if 'digital_addiction_score' in num_vars else 0)
    with col2:
        y_var = st.selectbox('Eixo Y:', num_vars,
                             index=num_vars.index('wellbeing_index')
                             if 'wellbeing_index' in num_vars else 1)
    with col3:
        cat_vars = [c for c in ['user_persona', 'age_group', 'gender',
                                'country', 'screen_time_cat']
                    if c in df.columns]
        color_var = st.selectbox('Cor:', cat_vars)

    trendline = st.checkbox('Mostrar linha de tendência', value=True)

    sample_exp = df.sample(n=min(5000, len(df)), random_state=42)
    fig_exp = px.scatter(
        sample_exp, x=x_var, y=y_var,
        color=color_var,
        trendline='ols' if trendline else None,
        color_discrete_sequence=INSTA_COLORS,
        title=f'{x_var} × {y_var}',
        template='plotly_dark', opacity=0.5,
        hover_data=['age', 'gender'] if 'age' in df.columns else None
    )
    fig_exp.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e',
                          height=550)
    st.plotly_chart(fig_exp, use_container_width=True)

# ── Tab 5: Assimetria ────────────────────────────────────────
with tab5:
    st.subheader('📈 Assimetria e Curtose')

    from scipy.stats import skew, kurtosis

    all_num = [v for v in USAGE_VARS + WELLBEING_VARS if v in df.columns]
    sk_vals = [skew(df[v].dropna())     for v in all_num]
    ku_vals = [kurtosis(df[v].dropna()) for v in all_num]

    col1, col2 = st.columns(2)

    with col1:
        cores_sk = ['#fd1d1d' if abs(s) > 1
                    else '#fcb045' if abs(s) > 0.5
                    else '#833ab4' for s in sk_vals]
        fig_sk = go.Figure(go.Bar(
            x=sk_vals, y=all_num,
            orientation='h',
            marker_color=cores_sk
        ))
        fig_sk.add_vline(x=0,  line_color='white', line_dash='dash')
        fig_sk.add_vline(x=1,  line_color='#fd1d1d', line_dash='dot')
        fig_sk.add_vline(x=-1, line_color='#fd1d1d', line_dash='dot')
        fig_sk.update_layout(
            title='Assimetria (Skewness)',
            template='plotly_dark',
            paper_bgcolor='#0f0f0f',
            height=500
        )
        st.plotly_chart(fig_sk, use_container_width=True)

    with col2:
        cores_ku = ['#fd1d1d' if abs(k) > 2
                    else '#fcb045' if abs(k) > 1
                    else '#833ab4' for k in ku_vals]
        fig_ku = go.Figure(go.Bar(
            x=ku_vals, y=all_num,
            orientation='h',
            marker_color=cores_ku
        ))
        fig_ku.add_vline(x=0, line_color='white', line_dash='dash')
        fig_ku.update_layout(
            title='Curtose (Kurtosis)',
            template='plotly_dark',
            paper_bgcolor='#0f0f0f',
            height=500
        )
        st.plotly_chart(fig_ku, use_container_width=True)