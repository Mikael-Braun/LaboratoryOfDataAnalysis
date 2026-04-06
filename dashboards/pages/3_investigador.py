import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import skew, kurtosis
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_utils import (load_data, sidebar_filters, apply_neon_style, page_header,
                        section_title, clinical_note, PLOTLY_BASE, plotly_axes,
                        INSTA_COLORS, NEON_GREEN, NEON_RED, NEON_YELLOW, USAGE_VARS, WELLBEING_VARS,
                        BG_MAIN, BG_SURFACE, TEXT_DIM)

st.set_page_config(page_title='Investigador', layout='wide', page_icon='🔬')
apply_neon_style(NEON_GREEN)

with st.sidebar:
    st.html(f"<p style='color:{NEON_GREEN}; font-size:0.7em; text-transform:uppercase; letter-spacing:0.15em; font-weight:700;'>⚙️ Configuração</p>")
    sample = st.select_slider('Amostra', [10_000, 25_000, 50_000, 100_000], value=50_000)
    st.divider()
    st.html(f"<p style='color:#444466; font-size:0.7em; text-transform:uppercase; letter-spacing:0.1em;'>Filtros</p>")

# Carregar amostra ajustada para compensar perdas nos filtros
adjusted_sample = min(273_788, int(sample * 1.05))
df = load_data(adjusted_sample)
df = sidebar_filters(df, accent=NEON_GREEN)
# Garantir exatamente o tamanho selecionado
if len(df) > sample:
    df = df.sample(n=sample, random_state=42)

page_header('🔬', 'Dashboard — Investigador', 'Análise Estatística Completa',
            '"Os dados revelam o que o olho não vê"', NEON_GREEN)

st.page_link('app.py', label='← 🏡', use_container_width=False)

st.info(f'📊 A analisar **{len(df):,} utilizadores** com os filtros actuais')

# ── KPIs ─────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
for col, label, key, fmt in zip(
    [c1,c2,c3,c4,c5],
    ['⏱️ Tempo Médio/Dia','😰 Stress Médio','😊 Felicidade','💚 Wellbeing','🎯 Addiction'],
    ['daily_active_minutes_instagram','perceived_stress_score','self_reported_happiness','wellbeing_index','digital_addiction_score'],
    ['{:.0f} min','{:.1f}','{:.2f}','{:.1f}/100','{:.1f}/100']
):
    if key in df.columns:
        col.metric(label, fmt.format(df[key].mean()))

st.divider()

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    '📊 DISTRIBUIÇÕES', '🔗 CORRELAÇÕES', '📐 ESTATÍSTICAS', '🔍 EXPLORADOR', '📈 ASSIMETRIA'
])

# Tab 1 — Distribuições
with tab1:
    section_title('Distribuições das Variáveis Principais', NEON_GREEN)
    col1, col2 = st.columns([2, 1])
    with col1:
        var_dist = st.selectbox('Variável:', [v for v in USAGE_VARS + WELLBEING_VARS if v in df.columns])
    with col2:
        n_bins = st.slider('Nº de bins:', 20, 100, 50)

    s = df[var_dist].dropna()
    fig = px.histogram(df, x=var_dist, nbins=n_bins, marginal='box',
                       color_discrete_sequence=[NEON_GREEN],
                       title=f'Distribuição: {var_dist.replace("_"," ").title()}',
                       template='plotly_dark')
    fig.add_vline(x=s.mean(), line_dash='dash', line_color='white',
                  annotation_text=f'μ = {s.mean():.2f}', annotation_font_color='white')
    fig.add_vline(x=s.median(), line_dash='dot', line_color=NEON_GREEN,
                  annotation_text=f'Med = {s.median():.2f}', annotation_font_color=NEON_GREEN)
    fig.update_layout(**PLOTLY_BASE)
    plotly_axes(fig)
    st.plotly_chart(fig, use_container_width=True)

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col, lbl, val in zip([c1,c2,c3,c4,c5,c6],
        ['Média','Mediana','D.P.','Mínimo','Máximo','IQR'],
        [s.mean(), s.median(), s.std(), s.min(), s.max(), s.quantile(0.75)-s.quantile(0.25)]):
        col.metric(lbl, f'{val:.3f}')

    clinical_note(f'Assimetria: {skew(s):.3f} | Curtose: {kurtosis(s):.3f} — '
                  f'{"Distribuição aproximadamente simétrica." if abs(skew(s)) < 0.5 else "Distribuição assimétrica — presença de outliers."}',
                  NEON_GREEN)

# Tab 2 — Correlações
with tab2:
    section_title('Mapa de Correlações', NEON_GREEN)
    num_cols = df.select_dtypes(include='number').columns.tolist()
    default_cols = [c for c in [
        'daily_active_minutes_instagram','perceived_stress_score',
        'self_reported_happiness','sleep_hours_per_night',
        'wellbeing_index','digital_addiction_score',
        'reels_watched_per_day','exercise_hours_per_week'
    ] if c in num_cols]

    col1, col2 = st.columns([3,1])
    with col1:
        sel_cols = st.multiselect('Variáveis:', options=num_cols, default=default_cols)
    with col2:
        metodo = st.radio('Método:', ['pearson','spearman'], horizontal=True)

    if len(sel_cols) >= 2:
        corr = df[sel_cols].corr(method=metodo)
        fig = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns.tolist(), y=corr.index.tolist(),
            colorscale='RdBu_r', zmid=0, zmin=-1, zmax=1,
            text=corr.round(2).values, texttemplate='%{text:.2f}',
            textfont=dict(size=9),
            hovertemplate='%{y} vs %{x}<br>r = %{z:.3f}<extra></extra>',
            showscale=True
        ))
        fig.update_layout(title=f'Correlações de {metodo.title()}',
                  height=550, **{**PLOTLY_BASE, 'margin': dict(l=120, r=20, t=50, b=120)})
        fig.update_xaxes(tickangle=-40, tickfont=dict(size=9))
        fig.update_yaxes(tickfont=dict(size=9))
        st.plotly_chart(fig, use_container_width=True)

        # Top correlações
        pairs = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack().reset_index()
        pairs.columns = ['Var A', 'Var B', 'r']
        pairs['|r|'] = pairs['r'].abs()
        pairs = pairs.sort_values('|r|', ascending=False)

        col1, col2 = st.columns(2)
        with col1:
            section_title('Top 5 Correlações Positivas', NEON_GREEN)
            st.dataframe(pairs[pairs['r'] > 0].head(5)[['Var A','Var B','r']].round(4),
                        use_container_width=True, hide_index=True)
        with col2:
            section_title('Top 5 Correlações Negativas', '#ff4466')
            st.dataframe(pairs[pairs['r'] < 0].head(5)[['Var A','Var B','r']].round(4),
                        use_container_width=True, hide_index=True)

# Tab 3 — Estatísticas
with tab3:
    section_title('Estatísticas Descritivas Completas', NEON_GREEN)
    grupo = st.radio('Grupo:', ['Uso do Instagram','Bem-Estar','Todas'], horizontal=True)

    if grupo == 'Uso do Instagram':
        vars_sel = [v for v in USAGE_VARS if v in df.columns]
    elif grupo == 'Bem-Estar':
        vars_sel = [v for v in WELLBEING_VARS if v in df.columns]
    else:
        vars_sel = [v for v in USAGE_VARS + WELLBEING_VARS if v in df.columns]

    rows = []
    for col in vars_sel:
        s = df[col].dropna()
        rows.append({
            'Variável': col, 'Média': round(s.mean(),3), 'Mediana': round(s.median(),3),
            'D.P.': round(s.std(),3), 'Variância': round(s.var(),3),
            'Mínimo': round(s.min(),3), 'Máximo': round(s.max(),3),
            'Q1': round(s.quantile(0.25),3), 'Q3': round(s.quantile(0.75),3),
            'IQR': round(s.quantile(0.75)-s.quantile(0.25),3),
            'Assimetria': round(skew(s),3), 'Curtose': round(kurtosis(s),3),
        })
    st.dataframe(pd.DataFrame(rows).set_index('Variável'), use_container_width=True, height=400)

# Tab 4 — Explorador de Variáveis (inspirado no doctor.py)
with tab4:
    section_title('Explorador de Variáveis', NEON_GREEN)
    num_vars  = df.select_dtypes(include='number').columns.tolist()
    cat_vars  = [c for c in ['user_persona','age_group','gender','country','screen_time_cat'] if c in df.columns]
    chart_types = ['Scatter','Box','Violin','Histograma']

    col1,col2,col3,col4,col5 = st.columns(5)
    with col1: x_var = st.selectbox('Eixo X:', num_vars, index=num_vars.index('digital_addiction_score') if 'digital_addiction_score' in num_vars else 0)
    with col2: y_var = st.selectbox('Eixo Y:', num_vars, index=num_vars.index('wellbeing_index') if 'wellbeing_index' in num_vars else 1)
    with col3: color_var = st.selectbox('Cor:', cat_vars)
    with col4: chart_type = st.selectbox('Tipo:', chart_types)
    with col5: sample_n = st.slider('Amostra:', 500, min(10_000, len(df)), 3000, step=500)

    s = df.sample(n=min(sample_n, len(df)), random_state=42)

    if chart_type == 'Scatter':
        fig = px.scatter(s, x=x_var, y=y_var, color=color_var,
                         color_discrete_sequence=INSTA_COLORS,
                         trendline='ols', trendline_scope='overall',
                         trendline_color_override='rgba(255,255,255,0.6)',
                         opacity=0.5, title=f'{x_var} × {y_var}',
                         template='plotly_dark')
    elif chart_type == 'Box':
        fig = px.box(s, x=color_var, y=y_var, color=color_var,
                     color_discrete_sequence=INSTA_COLORS,
                     title=f'{y_var} por {color_var}', template='plotly_dark')
    elif chart_type == 'Violin':
        fig = px.violin(s, x=color_var, y=y_var, color=color_var,
                        color_discrete_sequence=INSTA_COLORS, box=True,
                        title=f'{y_var} por {color_var}', template='plotly_dark')
    else:
        fig = px.histogram(s, x=x_var, color=color_var,
                           color_discrete_sequence=INSTA_COLORS, nbins=50,
                           title=f'Distribuição: {x_var}', template='plotly_dark')

    fig.update_layout(**PLOTLY_BASE, height=500)
    plotly_axes(fig)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander('📋 Ver dados filtrados'):
        cols_show = st.multiselect('Colunas:', df.columns.tolist(),
                                   default=[x_var, y_var, color_var])
        st.dataframe(df[cols_show].head(500), use_container_width=True, height=300)
        st.caption(f'{len(df):,} registos — a mostrar até 500.')

# Tab 5 — Assimetria
with tab5:
    section_title('Assimetria e Curtose', NEON_GREEN)
    all_vars = [v for v in USAGE_VARS + WELLBEING_VARS if v in df.columns]
    sk_vals = [skew(df[v].dropna())     for v in all_vars]
    ku_vals = [kurtosis(df[v].dropna()) for v in all_vars]

    col1, col2 = st.columns(2)
    with col1:
        cores = [NEON_RED if abs(s)>1 else NEON_YELLOW if abs(s)>0.5 else NEON_GREEN for s in sk_vals]
        fig = go.Figure(go.Bar(x=sk_vals, y=all_vars, orientation='h', marker_color=cores))
        fig.add_vline(x=0, line_color='white', line_dash='dash')
        fig.add_vline(x=1, line_color=NEON_RED, line_dash='dot')
        fig.add_vline(x=-1, line_color=NEON_RED, line_dash='dot')
        fig.update_layout(title='Assimetria (Skewness)', height=500, **PLOTLY_BASE)
        plotly_axes(fig)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        cores2 = [NEON_RED if abs(k)>2 else NEON_YELLOW if abs(k)>1 else NEON_GREEN for k in ku_vals]
        fig2 = go.Figure(go.Bar(x=ku_vals, y=all_vars, orientation='h', marker_color=cores2))
        fig2.add_vline(x=0, line_color='white', line_dash='dash')
        fig2.update_layout(title='Curtose (Kurtosis)', height=500, **PLOTLY_BASE)
        plotly_axes(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    clinical_note('Distribuições com curtose próxima de -1.2 (como stress e felicidade) '
                  'indicam uma geração sintética uniforme — em dados reais esperaríamos '
                  'distribuições mais naturais com concentração em valores centrais.', NEON_GREEN)

st.html(f"<p style='color:#1a1a2e; font-size:0.8em; text-align:center; margin-top:3rem;'>🔬 Dashboard Investigador · LAD 2025/26</p>")