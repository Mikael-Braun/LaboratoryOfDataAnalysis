# ============================================================
# DASHBOARD 4 — GESTOR DE MARKETING
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_utils import load_data, sidebar_filters, apply_style, INSTA_COLORS

st.set_page_config(page_title='📊 Marketing', layout='wide', page_icon='📊')
apply_style()

st.title('📊 Dashboard — Gestor de Marketing')
st.markdown('*Personas, engagement, conteúdo preferido e comportamento por mercado*')
st.divider()

with st.sidebar:
    st.header('⚙️ Configuração')
    sample = st.select_slider('Amostra', [10_000, 25_000, 50_000, 100_000], 50_000)
    st.divider()

df = load_data(sample)
df = sidebar_filters(df, show_screen_time=False)

st.info(f'📊 A analisar **{len(df):,} utilizadores**')

# KPIs de marketing
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric('⏱️ Tempo Médio/Dia',
            f'{df["daily_active_minutes_instagram"].mean():.0f} min')
col2.metric('🎯 Engagement Score',
            f'{df["user_engagement_score"].mean():.2f}')
col3.metric('👥 Seguidores Médios',
            f'{df["followers_count"].mean():.0f}')
col4.metric('📱 Sessões/Dia',
            f'{df["sessions_per_day"].mean():.1f}')
col5.metric('💎 Utilizadores Premium',
            f'{(df["subscription_status"]=="Premium").mean()*100:.1f}%'
            if 'subscription_status' in df.columns else 'N/A')

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    '👥 Personas',
    '📱 Conteúdo & Engagement',
    '🌍 Análise por Mercado',
    '💎 Premium vs Free'
])

# ── Tab 1: Personas ──────────────────────────────────────────
with tab1:
    st.subheader('👥 Segmentação de Utilizadores por Persona')

    col1, col2 = st.columns(2)

    with col1:
        persona_counts = df['user_persona'].value_counts()
        fig = px.pie(
            persona_counts.reset_index(),
            names='user_persona', values='count',
            title='Distribuição de Personas',
            color_discrete_sequence=INSTA_COLORS,
            template='plotly_dark', hole=0.4
        )
        fig.update_layout(paper_bgcolor='#0f0f0f')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Engagement por persona
        eng_persona = df.groupby('user_persona').agg(
            engagement=('user_engagement_score', 'mean'),
            followers=('followers_count', 'mean'),
            minutos=('daily_active_minutes_instagram', 'mean'),
            posts=('posts_created_per_week', 'mean')
        ).round(2).reset_index()

        fig2 = px.bar(
            eng_persona,
            x='user_persona', y='engagement',
            color='user_persona',
            color_discrete_sequence=INSTA_COLORS,
            title='Engagement Score Médio por Persona',
            template='plotly_dark',
            labels={'engagement': 'Engagement Score', 'user_persona': 'Persona'}
        )
        fig2.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e',
                           showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Tabela detalhada
    st.markdown('**📋 Perfil Detalhado por Persona:**')
    st.dataframe(eng_persona.set_index('user_persona'), use_container_width=True)

# ── Tab 2: Conteúdo & Engagement ─────────────────────────────
with tab2:
    st.subheader('📱 Análise de Conteúdo e Engagement')

    col1, col2 = st.columns(2)

    with col1:
        if 'content_type_preference' in df.columns:
            content_eng = df.groupby('content_type_preference').agg(
                engagement=('user_engagement_score', 'mean'),
                n=('user_engagement_score', 'count')
            ).reset_index()
            fig = px.bar(
                content_eng.sort_values('engagement', ascending=True),
                x='engagement', y='content_type_preference',
                orientation='h',
                color='engagement',
                color_continuous_scale='Viridis',
                title='Engagement por Tipo de Conteúdo',
                template='plotly_dark',
                labels={'content_type_preference': 'Tipo de Conteúdo',
                        'engagement': 'Engagement Médio'}
            )
            fig.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e')
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 'preferred_content_theme' in df.columns:
            theme_counts = df['preferred_content_theme'].value_counts().head(10)
            fig2 = px.bar(
                theme_counts.reset_index(),
                x='count', y='preferred_content_theme',
                orientation='h',
                color='count',
                color_continuous_scale='Purples',
                title='Top 10 Temas de Conteúdo',
                template='plotly_dark',
                labels={'preferred_content_theme': 'Tema', 'count': 'Nº Utilizadores'}
            )
            fig2.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e')
            st.plotly_chart(fig2, use_container_width=True)

    # Tempo por secção
    st.subheader('⏱️ Distribuição do Tempo por Secção')
    time_cols = [c for c in ['time_on_feed_per_day', 'time_on_reels_per_day',
                             'time_on_explore_per_day', 'time_on_messages_per_day']
                 if c in df.columns]
    if time_cols:
        time_means = df[time_cols].mean()
        labels = [c.replace('time_on_','').replace('_per_day','').title()
                  for c in time_cols]
        fig3 = px.pie(
            values=time_means.values, names=labels,
            title='Tempo Médio por Secção do Instagram',
            color_discrete_sequence=INSTA_COLORS,
            template='plotly_dark', hole=0.3
        )
        fig3.update_layout(paper_bgcolor='#0f0f0f')
        st.plotly_chart(fig3, use_container_width=True)

# ── Tab 3: Análise por Mercado ───────────────────────────────
with tab3:
    st.subheader('🌍 Performance por Mercado (País)')

    if 'country' in df.columns:
        metrica = st.selectbox(
            'Métrica a analisar:',
            [c for c in ['user_engagement_score', 'daily_active_minutes_instagram',
                         'followers_count', 'posts_created_per_week',
                         'digital_addiction_score']
             if c in df.columns]
        )

        country_stats = df.groupby('country').agg(
            valor=(metrica, 'mean'),
            n=('user_engagement_score', 'count')
        ).reset_index().sort_values('valor', ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                country_stats,
                x='valor', y='country',
                orientation='h',
                color='valor',
                color_continuous_scale='Viridis',
                title=f'{metrica.replace("_"," ").title()} por País',
                template='plotly_dark',
                text='valor',
                labels={'valor': metrica, 'country': 'País'}
            )
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.bar(
                country_stats,
                x='country', y='n',
                color='n',
                color_continuous_scale='Purples',
                title='Nº de Utilizadores por País',
                template='plotly_dark',
                labels={'country': 'País', 'n': 'Nº Utilizadores'}
            )
            fig2.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e')
            st.plotly_chart(fig2, use_container_width=True)

# ── Tab 4: Premium vs Free ───────────────────────────────────
with tab4:
    st.subheader('💎 Análise Premium vs Free')

    if 'subscription_status' in df.columns:
        col1, col2 = st.columns(2)

        sub_counts = df['subscription_status'].value_counts()
        with col1:
            fig = px.pie(
                sub_counts.reset_index(),
                names='subscription_status', values='count',
                title='Distribuição Free vs Premium',
                color_discrete_sequence=INSTA_COLORS,
                template='plotly_dark', hole=0.4
            )
            fig.update_layout(paper_bgcolor='#0f0f0f')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            metricas_sub = df.groupby('subscription_status').agg(
                engagement=('user_engagement_score', 'mean'),
                minutos=('daily_active_minutes_instagram', 'mean'),
                seguidores=('followers_count', 'mean'),
                posts=('posts_created_per_week', 'mean')
            ).round(2)
            st.markdown('**Perfil médio por tipo de subscrição:**')
            st.dataframe(metricas_sub, use_container_width=True)

        # Engagement por subscrição e persona
        eng_sub_persona = df.groupby(
            ['subscription_status', 'user_persona']
        )['user_engagement_score'].mean().reset_index()

        fig3 = px.bar(
            eng_sub_persona,
            x='user_persona', y='user_engagement_score',
            color='subscription_status',
            barmode='group',
            color_discrete_sequence=INSTA_COLORS,
            title='Engagement por Persona e Tipo de Subscrição',
            template='plotly_dark',
            labels={'user_persona': 'Persona',
                    'user_engagement_score': 'Engagement Score',
                    'subscription_status': 'Subscrição'}
        )
        fig3.update_layout(paper_bgcolor='#0f0f0f', plot_bgcolor='#1a1a2e')
        st.plotly_chart(fig3, use_container_width=True)