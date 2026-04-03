# ============================================================
# DASHBOARD 2 — PROFISSIONAL DE SAÚDE
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_utils import (load_data, sidebar_filters, render_kpis,
                        apply_style, INSTA_COLORS)

st.set_page_config(page_title='🧑‍⚕️ Saúde', layout='wide', page_icon='🧑‍⚕️')
apply_style()

st.title('🧑‍⚕️ Dashboard — Profissional de Saúde')
st.markdown('*Indicadores de risco, grupos vulneráveis e impacto na saúde mental*')
st.divider()

with st.sidebar:
    st.header('⚙️ Configuração')
    sample = st.select_slider('Amostra', [10_000, 25_000, 50_000, 100_000], 50_000)
    st.divider()

df = load_data(sample)
df = sidebar_filters(df, show_screen_time=False)

st.info(f'📊 A analisar **{len(df):,} utilizadores**')
render_kpis(df)
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    '🚨 Grupos de Risco',
    '😰 Stress & Uso',
    '😴 Sono & Bem-Estar',
    '📋 Indicadores Clínicos'
])

# ── Tab 1: Grupos de Risco ───────────────────────────────────
with tab1:
    st.subheader('🚨 Identificação de Grupos de Risco')

    # Limiar de risco configurável
    col1, col2 = st.columns(2)
    with col1:
        limiar_stress = st.slider(
            'Limiar de Stress Alto (0-40):', 0, 40, 25
        )
    with col2:
        limiar_uso = st.slider(
            'Limiar de Uso Excessivo (min/dia):', 60, 400, 240
        )

    # Classifica utilizadores
    df['risco_stress'] = df['perceived_stress_score'] >= limiar_stress
    df['risco_uso']    = df['daily_active_minutes_instagram'] >= limiar_uso
    df['alto_risco']   = df['risco_stress'] & df['risco_uso']

    n_risco = df['alto_risco'].sum()
    pct_risco = n_risco / len(df) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric('🚨 Alto Risco', f'{n_risco:,}', f'{pct_risco:.1f}%')
    col2.metric('😰 Stress Alto',
                f'{df["risco_stress"].sum():,}',
                f'{df["risco_stress"].mean()*100:.1f}%')
    col3.metric('📱 Uso Excessivo',
                f'{df["risco_uso"].sum():,}',
                f'{df["risco_uso"].mean()*100:.1f}%')
    col4.metric('💚 Wellbeing Médio',
                f'{df[df["alto_risco"]]["wellbeing_index"].mean():.1f}/100')

    st.divider()

    # Risco por faixa etária
    if 'age_group' in df.columns:
        col1, col2 = st.columns(2)
        with col1:
            risco_idade = df.groupby('age_group')['alto_risco'].mean() * 100
            fig = px.bar(
                risco_idade.reset_index(),
                x='age_group', y='alto_risco',
                title='% Alto Risco por Faixa Etária',
                color='alto_risco',
                color_continuous_scale='RdYlGn_r',
                template='plotly_dark',
                labels={'alto_risco': '% Alto Risco', 'age_group': 'Faixa Etária'}
            )
            fig.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'gender' in df.columns:
                risco_gen = df.groupby('gender')['alto_risco'].mean() * 100
                fig2 = px.pie(
                    risco_gen.reset_index(),
                    names='gender', values='alto_risco',
                    title='% Alto Risco por Género',
                    color_discrete_sequence=INSTA_COLORS,
                    template='plotly_dark'
                )
                fig2.update_layout(paper_bgcolor='#0f0f0f')
                st.plotly_chart(fig2, use_container_width=True)

# ── Tab 2: Stress & Uso ──────────────────────────────────────
with tab2:
    st.subheader('😰 Relação entre Stress e Uso do Instagram')

    col1, col2 = st.columns(2)

    with col1:
        # Violin plot stress vs uso
        if 'screen_time_cat' in df.columns:
            fig = px.violin(
                df, x='screen_time_cat', y='perceived_stress_score',
                color='screen_time_cat',
                color_discrete_sequence=INSTA_COLORS,
                title='Stress por Categoria de Tempo de Ecrã',
                template='plotly_dark', box=True,
                category_orders={'screen_time_cat': [
                    'Mínimo (<30min)', 'Baixo (30-60min)',
                    'Moderado (1-2h)', 'Alto (2-4h)', 'Excessivo (>4h)'
                ]}
            )
            fig.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e',
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Scatter stress vs doom scroll
        if 'doom_scroll_ratio' in df.columns:
            sample_plot = df.sample(n=min(3000, len(df)), random_state=42)
            fig2 = px.scatter(
                sample_plot,
                x='doom_scroll_ratio',
                y='perceived_stress_score',
                color='perceived_stress_score',
                color_continuous_scale='RdYlGn_r',
                trendline='ols',
                title='Doom Scroll Ratio vs Stress',
                template='plotly_dark', opacity=0.5,
                labels={
                    'doom_scroll_ratio': 'Doom Scroll Ratio',
                    'perceived_stress_score': 'Stress Score'
                }
            )
            fig2.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e')
            st.plotly_chart(fig2, use_container_width=True)

    # Média de stress por persona
    if 'user_persona' in df.columns:
        st.subheader('Stress Médio por Persona')
        stress_persona = (
            df.groupby('user_persona')[
                ['perceived_stress_score', 'wellbeing_index',
                 'digital_addiction_score']
            ].mean().round(2)
        )
        st.dataframe(stress_persona, use_container_width=True)

# ── Tab 3: Sono & Bem-Estar ──────────────────────────────────
with tab3:
    st.subheader('😴 Qualidade do Sono e Bem-Estar')

    col1, col2 = st.columns(2)

    with col1:
        if 'sleep_quality' in df.columns:
            sleep_wb = df.groupby('sleep_quality')[
                ['wellbeing_index', 'perceived_stress_score',
                 'self_reported_happiness']
            ].mean().reset_index()

            fig = px.bar(
                sleep_wb, x='sleep_quality', y='wellbeing_index',
                color='wellbeing_index',
                color_continuous_scale='RdYlGn',
                title='Wellbeing Index por Qualidade do Sono',
                template='plotly_dark',
                labels={'sleep_quality': 'Qualidade do Sono',
                        'wellbeing_index': 'Wellbeing Index'}
            )
            fig.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e')
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Uso do Instagram vs sono
        sample_sleep = df.sample(n=min(3000, len(df)), random_state=42)
        fig2 = px.scatter(
            sample_sleep,
            x='daily_active_minutes_instagram',
            y='sleep_hours_per_night',
            color='perceived_stress_score',
            color_continuous_scale='RdYlGn_r',
            trendline='ols',
            title='Uso Instagram vs Sono',
            template='plotly_dark', opacity=0.4,
            labels={
                'daily_active_minutes_instagram': 'Minutos/Dia no Instagram',
                'sleep_hours_per_night': 'Horas de Sono'
            }
        )
        fig2.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e')
        st.plotly_chart(fig2, use_container_width=True)

# ── Tab 4: Indicadores Clínicos ──────────────────────────────
with tab4:
    st.subheader('📋 Indicadores Clínicos por Grupo')

    group_by = st.selectbox(
        'Agrupar por:',
        [c for c in ['age_group', 'gender', 'country', 'user_persona',
                     'screen_time_cat', 'sleep_quality']
         if c in df.columns]
    )

    indicadores = [c for c in [
        'perceived_stress_score', 'self_reported_happiness',
        'sleep_hours_per_night', 'exercise_hours_per_week',
        'body_mass_index', 'blood_pressure_systolic',
        'daily_steps_count', 'wellbeing_index'
    ] if c in df.columns]

    tabela = df.groupby(group_by)[indicadores].mean().round(2)
    st.dataframe(tabela, use_container_width=True)

    # Heatmap
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    tabela_norm = pd.DataFrame(
        scaler.fit_transform(tabela),
        index=tabela.index, columns=tabela.columns
    )
    fig_heat = px.imshow(
        tabela_norm, text_auto='.2f',
        color_continuous_scale='RdYlGn',
        title=f'Indicadores Clínicos Normalizados por {group_by}',
        template='plotly_dark', aspect='auto'
    )
    fig_heat.update_layout(paper_bgcolor='#0f0f0f', height=500)
    st.plotly_chart(fig_heat, use_container_width=True)