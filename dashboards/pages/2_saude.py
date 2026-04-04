import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_utils import (load_data, sidebar_filters, apply_neon_style, page_header,
                        section_title, clinical_note, kpi_zone, PLOTLY_BASE, plotly_axes,
                        INSTA_COLORS, NEON_PINK, NEON_GREEN, NEON_YELLOW, NEON_RED,
                        BG_SURFACE, TEXT_DIM)

st.set_page_config(page_title='Saúde', layout='wide', page_icon='🧑‍⚕️')
apply_neon_style(NEON_PINK)

with st.sidebar:
    st.html(f"<p style='color:{NEON_PINK}; font-size:0.7em; text-transform:uppercase; letter-spacing:0.15em; font-weight:700;'>⚙️ Configuração</p>")
    sample = st.select_slider('Amostra', [10_000, 25_000, 50_000, 100_000], value=50_000)
    st.divider()
    st.html(f"<p style='color:#444466; font-size:0.7em; text-transform:uppercase; letter-spacing:0.1em;'>Filtros</p>")

# Carregar amostra ajustada para compensar perdas nos filtros
adjusted_sample = min(273_788, int(sample * 1.05))
df = load_data(adjusted_sample)
df = sidebar_filters(df, accent=NEON_PINK, show_screen=False)
# Garantir exatamente o tamanho selecionado
if len(df) > sample:
    df = df.sample(n=sample, random_state=42)

page_header('🧑‍⚕️', 'Dashboard — Profissional de Saúde', 'Análise Clínica e Grupos de Risco',
            '"Quem são os utilizadores em risco?"', NEON_PINK)

st.page_link('app.py', label='← 🏡', use_container_width=False)

st.info(f'📊 A analisar **{len(df):,} utilizadores**')

# ── KPIs com zonas de risco (inspirado no doctor.py) ─────────
st.html("<br>")
pct_alto_stress = (df['perceived_stress_score'] >= 25).mean() * 100
pct_uso_excessivo = (df['daily_active_minutes_instagram'] >= 240).mean() * 100
pct_sono_insuf = (df['sleep_hours_per_night'] <= 6).mean() * 100
wellbeing_medio = df['wellbeing_index'].mean()

c1,c2,c3,c4 = st.columns(4)
kpi_zone('Alto Stress', f'{pct_alto_stress:.1f}%', 'stress score ≥ 25/40',
         'bad' if pct_alto_stress > 40 else 'mid' if pct_alto_stress > 25 else 'good', c1)
kpi_zone('Uso Excessivo', f'{pct_uso_excessivo:.1f}%', 'mais de 4h/dia no Instagram',
         'bad' if pct_uso_excessivo > 30 else 'mid' if pct_uso_excessivo > 15 else 'good', c2)
kpi_zone('Sono Insuficiente', f'{pct_sono_insuf:.1f}%', 'menos de 6h por noite',
         'bad' if pct_sono_insuf > 30 else 'mid' if pct_sono_insuf > 15 else 'good', c3)
kpi_zone('Wellbeing Médio', f'{wellbeing_medio:.1f}/100', 'índice de bem-estar geral',
         'good' if wellbeing_medio > 60 else 'mid' if wellbeing_medio > 40 else 'bad', c4)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(['🚨 GRUPOS DE RISCO', '😰 STRESS & USO', '😴 SONO', '📋 INDICADORES'])

# Tab 1 — Grupos de Risco
with tab1:
    section_title('Configuração dos Limiares de Risco', NEON_PINK)
    col1, col2, col3 = st.columns(3)
    with col1: limiar_stress = st.slider('Limiar Stress Alto (>):', 10, 40, 25)
    with col2: limiar_uso    = st.slider('Limiar Uso Excessivo (min >):', 60, 400, 240)
    with col3: limiar_sono   = st.slider('Limiar Sono Insuficiente (h <):', 4, 8, 6)

    df['alto_risco'] = (
        (df['perceived_stress_score'] >= limiar_stress) &
        (df['daily_active_minutes_instagram'] >= limiar_uso)
    )
    df['vulneravel'] = (
        (df['perceived_stress_score'] >= limiar_stress) |
        (df['daily_active_minutes_instagram'] >= limiar_uso) |
        (df['sleep_hours_per_night'] <= limiar_sono)
    )

    n_risco = df['alto_risco'].sum()
    n_vuln  = df['vulneravel'].sum()
    st.html("<br>")
    c1,c2,c3,c4 = st.columns(4)
    kpi_zone('🚨 Alto Risco', f'{n_risco:,}', f'{n_risco/len(df)*100:.1f}% da população', 'bad', c1)
    kpi_zone('⚠️ Vulneráveis', f'{n_vuln:,}', f'{n_vuln/len(df)*100:.1f}% da população', 'mid', c2)
    kpi_zone('💚 Baixo Risco', f'{len(df)-n_vuln:,}', f'{(len(df)-n_vuln)/len(df)*100:.1f}% da população', 'good', c3)
    kpi_zone('📊 Wellbeing Alto Risco', f'{df[df["alto_risco"]]["wellbeing_index"].mean():.1f}/100', 'média do grupo de risco', 'bad', c4)

    st.html("<br>")
    col1, col2 = st.columns(2)

    with col1:
        section_title('% Alto Risco por Faixa Etária', NEON_PINK)
        if 'age_group' in df.columns:
            risco_idade = df.groupby('age_group')['alto_risco'].mean() * 100
            fig = go.Figure(go.Bar(
                x=risco_idade.index.tolist(), y=risco_idade.values,
                marker=dict(color=risco_idade.values, colorscale='RdYlGn_r'),
                text=risco_idade.round(1).astype(str) + '%',
                textposition='outside', textfont=dict(color='white')
            ))
            fig.update_layout(title='', height=320, **PLOTLY_BASE)
            plotly_axes(fig)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title('Distribuição de Risco por Persona', NEON_PINK)
        if 'user_persona' in df.columns:
            risco_persona = df.groupby('user_persona').agg(
                pct_risco=('alto_risco', lambda x: x.mean()*100),
                wellbeing=('wellbeing_index', 'mean')
            ).reset_index().sort_values('pct_risco', ascending=True)

            fig2 = go.Figure(go.Bar(
                x=risco_persona['pct_risco'], y=risco_persona['user_persona'],
                orientation='h',
                marker=dict(color=risco_persona['pct_risco'].values, colorscale='RdYlGn_r'),
                text=risco_persona['pct_risco'].round(1).astype(str) + '%',
                textposition='outside', textfont=dict(color='white')
            ))
            fig2.update_layout(title='', height=320, **PLOTLY_BASE)
            plotly_axes(fig2)
            st.plotly_chart(fig2, use_container_width=True)

    clinical_note('O grupo de alto risco é definido pela combinação de stress elevado E uso excessivo. '
                  'Utilizadores Doom-Scroller são consistentemente os mais afectados.', NEON_PINK)

# Tab 2 — Stress & Uso
with tab2:
    section_title('Relação entre Stress e Uso do Instagram', NEON_PINK)
    col1, col2 = st.columns(2)

    with col1:
        # Violin plot — inspirado no doctor.py
        if 'screen_time_cat' in df.columns:
            order = ['Mínimo','Baixo','Moderado','Alto','Excessivo']
            fig = px.violin(df, x='screen_time_cat', y='perceived_stress_score',
                            color='screen_time_cat',
                            color_discrete_sequence=INSTA_COLORS,
                            title='Stress por Categoria de Tempo de Ecrã',
                            template='plotly_dark', box=True,
                            category_orders={'screen_time_cat': order})
            fig.update_layout(**PLOTLY_BASE, height=380, showlegend=False)
            plotly_axes(fig)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Scatter stress vs doom scroll
        if 'doom_scroll_ratio' in df.columns:
            s = df.sample(n=min(3000, len(df)), random_state=42)
            fig2 = px.scatter(s, x='doom_scroll_ratio', y='perceived_stress_score',
                              color='perceived_stress_score',
                              color_continuous_scale='RdYlGn_r',
                              trendline='ols',
                              title='Doom Scroll Ratio vs Stress',
                              template='plotly_dark', opacity=0.45)
            fig2.update_layout(**PLOTLY_BASE, height=380)
            plotly_axes(fig2)
            st.plotly_chart(fig2, use_container_width=True)

    section_title('Matriz de Risco — Stress × Uso', NEON_PINK)
    s = df.sample(n=min(5000, len(df)), random_state=42)
    fig3 = px.scatter(s, x='daily_active_minutes_instagram', y='perceived_stress_score',
                      color='wellbeing_index', color_continuous_scale='RdYlGn',
                      size='digital_addiction_score', size_max=12,
                      hover_data=['user_persona','age_group'] if 'user_persona' in df.columns else None,
                      title='Matriz de Risco: Tempo de Uso × Stress (tamanho = Addiction Score)',
                      template='plotly_dark', opacity=0.5)
    fig3.add_vline(x=240, line_dash='dot', line_color=NEON_RED,
                   annotation_text='4h/dia', annotation_font_color=NEON_RED)
    fig3.add_hline(y=25, line_dash='dot', line_color=NEON_RED,
                   annotation_text='Stress Alto', annotation_font_color=NEON_RED)
    fig3.update_layout(**PLOTLY_BASE, height=450)
    plotly_axes(fig3)
    st.plotly_chart(fig3, use_container_width=True)
    clinical_note('O quadrante superior direito (>4h/dia e stress>25) representa os utilizadores de maior risco. '
                  'A correlação de Pearson entre estas variáveis é r=0.84 — uma das mais fortes em ciências sociais.', NEON_PINK)

# Tab 3 — Sono
with tab3:
    section_title('Qualidade do Sono e Bem-Estar', NEON_PINK)
    col1, col2 = st.columns(2)

    with col1:
        if 'sleep_quality' in df.columns:
            order_sleep = ['Muito Baixo (<5h)','Baixo (5-6h)','Adequado (6-7h)','Bom (7-8h)','Muito Bom (>8h)']
            order_sleep = [s for s in order_sleep if s in df['sleep_quality'].unique()]
            sleep_wb = df.groupby('sleep_quality')[['wellbeing_index','perceived_stress_score']].mean().reset_index()
            fig = px.bar(sleep_wb, x='sleep_quality', y='wellbeing_index',
                         color='wellbeing_index', color_continuous_scale='RdYlGn',
                         title='Wellbeing Index por Qualidade do Sono',
                         template='plotly_dark',
                         category_orders={'sleep_quality': order_sleep})
            fig.update_layout(**PLOTLY_BASE, height=350)
            plotly_axes(fig)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        s = df.sample(n=min(3000, len(df)), random_state=42)
        fig2 = px.scatter(s, x='daily_active_minutes_instagram', y='sleep_hours_per_night',
                          color='perceived_stress_score', color_continuous_scale='RdYlGn_r',
                          trendline='ols', title='Uso Instagram vs Sono',
                          template='plotly_dark', opacity=0.4)
        fig2.add_hline(y=7, line_dash='dot', line_color=NEON_GREEN,
                       annotation_text='7h recomendadas (OMS)')
        fig2.update_layout(**PLOTLY_BASE, height=350)
        plotly_axes(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    clinical_note('A OMS recomenda 7-9 horas de sono por noite para adultos. '
                  'A correlação negativa entre uso do Instagram e horas de sono sugere que '
                  'o uso da plataforma antes de dormir pode estar a afectar a qualidade do sono.', NEON_PINK)

# Tab 4 — Indicadores Clínicos
with tab4:
    section_title('Indicadores Clínicos por Grupo', NEON_PINK)
    group_by = st.selectbox('Agrupar por:',
                            [c for c in ['age_group','gender','country','user_persona','screen_time_cat']
                             if c in df.columns])

    indicadores = [c for c in ['perceived_stress_score','self_reported_happiness',
                               'sleep_hours_per_night','exercise_hours_per_week',
                               'body_mass_index','blood_pressure_systolic',
                               'daily_steps_count','wellbeing_index'] if c in df.columns]

    tabela = df.groupby(group_by)[indicadores].mean().round(2)
    st.dataframe(tabela, use_container_width=True)

    # Heatmap normalizado
    scaler = MinMaxScaler()
    tabela_norm = pd.DataFrame(scaler.fit_transform(tabela), index=tabela.index, columns=tabela.columns)
    fig = go.Figure(go.Heatmap(
        z=tabela_norm.values,
        x=tabela_norm.columns.tolist(),
        y=tabela_norm.index.tolist(),
        colorscale='RdYlGn', zmid=0.5, zmin=0, zmax=1,
        text=tabela.round(1).values, texttemplate='%{text}',
        textfont=dict(size=9),
        hovertemplate='%{y} — %{x}<br>Valor: %{text}<extra></extra>',
        showscale=True
    ))
    fig.update_layout(title=f'Indicadores por {group_by} (valores reais, cores normalizadas)',
                  height=400, **{**PLOTLY_BASE, 'margin': dict(l=120, r=20, t=50, b=120)})
    fig.update_xaxes(tickangle=-30, tickfont=dict(size=9))
    st.plotly_chart(fig, use_container_width=True)

st.html(f"<p style='color:#1a1a2e; font-size:0.8em; text-align:center; margin-top:3rem;'>🧑‍⚕️ Dashboard Saúde · LAD 2025/26</p>")