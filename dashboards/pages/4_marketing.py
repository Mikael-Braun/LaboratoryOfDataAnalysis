import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_utils import (load_data, sidebar_filters, apply_neon_style, page_header,
                        section_title, clinical_note, kpi_zone, PLOTLY_BASE, plotly_axes,
                        INSTA_COLORS, NEON_CYAN, NEON_GREEN, NEON_YELLOW, BG_SURFACE, TEXT_DIM)

st.set_page_config(page_title='Marketing', layout='wide', page_icon='📊')
apply_neon_style(NEON_CYAN)

with st.sidebar:
    st.html(f"<p style='color:{NEON_CYAN}; font-size:0.7em; text-transform:uppercase; letter-spacing:0.15em; font-weight:700;'>⚙️ Configuração</p>")
    sample = st.select_slider('Amostra', [10_000, 25_000, 50_000, 100_000], value=50_000)
    st.divider()
    st.html(f"<p style='color:#444466; font-size:0.7em; text-transform:uppercase; letter-spacing:0.1em;'>Filtros</p>")

# Carregar amostra ajustada para compensar perdas nos filtros
adjusted_sample = min(273_788, int(sample * 1.05))
df = load_data(adjusted_sample)
df = sidebar_filters(df, accent=NEON_CYAN, show_screen=False)
# Garantir exatamente o tamanho selecionado
if len(df) > sample:
    df = df.sample(n=sample, random_state=42)

page_header('📊', 'Dashboard — Gestor de Marketing', 'Personas & Comportamento Digital',
            '"Onde está a atenção?"', NEON_CYAN)

st.page_link('app.py', label='← 🏡', use_container_width=False)

st.info(f'📊 A analisar **{len(df):,} utilizadores**')

# ── KPIs ─────────────────────────────────────────────────────
st.html("<br>")
c1,c2,c3,c4,c5 = st.columns(5)
kpi_zone('⏱️ Tempo Médio/Dia', f'{df["daily_active_minutes_instagram"].mean():.0f} min',
         'tempo de atenção disponível', 'mid', c1)
kpi_zone('🎯 Engagement Score', f'{df["user_engagement_score"].mean():.2f}',
         'score médio de engagement', 'good', c2)
kpi_zone('👥 Seguidores Médios', f'{df["followers_count"].mean():.0f}',
         'alcance médio por utilizador', 'good', c3)
kpi_zone('📱 Sessões/Dia', f'{df["sessions_per_day"].mean():.1f}',
         'oportunidades de contacto diário', 'good', c4)
pct_premium = (df['subscription_status'] == 'Premium').mean()*100 if 'subscription_status' in df.columns else 0
kpi_zone('💎 Premium', f'{pct_premium:.1f}%', 'utilizadores com subscrição paga', 'mid', c5)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    '👥 PERSONAS', '📱 CONTEÚDO', '🌍 MERCADOS', '💎 PREMIUM'
])

# Tab 1 — Personas
with tab1:
    section_title('Segmentação por Persona', NEON_CYAN)
    col1, col2 = st.columns(2)

    with col1:
        persona_counts = df['user_persona'].value_counts().reset_index()
        persona_counts.columns = ['persona', 'count']
        fig = px.pie(persona_counts, names='persona', values='count',
                     title='Distribuição de Personas',
                     color_discrete_sequence=INSTA_COLORS,
                     template='plotly_dark', hole=0.45)
        fig.update_layout(**PLOTLY_BASE)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        eng_persona = df.groupby('user_persona').agg(
            engagement=('user_engagement_score','mean'),
            followers=('followers_count','mean'),
            minutos=('daily_active_minutes_instagram','mean'),
            posts=('posts_created_per_week','mean'),
            addiction=('digital_addiction_score','mean')
        ).round(2).reset_index().sort_values('engagement', ascending=True)

        fig2 = go.Figure(go.Bar(
            x=eng_persona['engagement'], y=eng_persona['user_persona'],
            orientation='h', marker_color=INSTA_COLORS[:len(eng_persona)],
            text=eng_persona['engagement'].round(2), textposition='outside',
            textfont=dict(color='white')
        ))
        fig2.update_layout(title='Engagement Score Médio por Persona', height=320, **PLOTLY_BASE)
        plotly_axes(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    section_title('Perfil Detalhado por Persona', NEON_CYAN)
    st.dataframe(eng_persona.set_index('user_persona'), use_container_width=True)

    # Heatmap de perfil das personas
    section_title('Matriz de Personas', NEON_CYAN)
    vars_radar = [c for c in ['digital_addiction_score','wellbeing_index','doom_scroll_ratio',
                              'user_engagement_score','followers_count'] if c in df.columns]
    from sklearn.preprocessing import MinMaxScaler
    perfil = df.groupby('user_persona')[vars_radar].mean()
    perfil_norm = pd.DataFrame(MinMaxScaler().fit_transform(perfil),
                               index=perfil.index, columns=perfil.columns)

    fig3 = go.Figure(go.Heatmap(
        z=perfil_norm.values, x=perfil_norm.columns.tolist(), y=perfil_norm.index.tolist(),
        colorscale='Viridis', zmin=0, zmax=1,
        text=perfil.round(1).values, texttemplate='%{text}',
        textfont=dict(size=10),
        hovertemplate='%{y} — %{x}<br>Valor: %{text}<extra></extra>'
    ))
    fig3.update_layout(title='Perfil Normalizado por Persona (valores reais nas células)',
                       height=350, **{**PLOTLY_BASE, 'margin': dict(l=140,r=20,t=50,b=80)})
    fig3.update_xaxes(tickangle=-20, tickfont=dict(size=9))
    st.plotly_chart(fig3, use_container_width=True)

    clinical_note('Os Doom-Scrollers representam o segmento mais valioso em termos de tempo de atenção, '
                  'mas também o mais vulnerável. Os Influencers/Creators têm menor addiction score mas '
                  'maior engagement — o segmento ideal para parcerias de conteúdo.', NEON_CYAN)

# Tab 2 — Conteúdo
with tab2:
    section_title('Análise de Conteúdo e Engagement', NEON_CYAN)
    col1, col2 = st.columns(2)

    with col1:
        if 'content_type_preference' in df.columns:
            content_eng = df.groupby('content_type_preference').agg(
                engagement=('user_engagement_score','mean'),
                n=('user_engagement_score','count')
            ).reset_index().sort_values('engagement', ascending=True)
            fig = go.Figure(go.Bar(
                x=content_eng['engagement'], y=content_eng['content_type_preference'],
                orientation='h',
                marker=dict(color=content_eng['engagement'].values, colorscale='Viridis'),
                text=content_eng['engagement'].round(2), textposition='outside',
                textfont=dict(color='white')
            ))
            fig.update_layout(title='Engagement por Tipo de Conteúdo', height=320, **PLOTLY_BASE)
            plotly_axes(fig)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 'preferred_content_theme' in df.columns:
            theme = df['preferred_content_theme'].value_counts().head(10).reset_index()
            theme.columns = ['tema','count']
            fig2 = go.Figure(go.Bar(
                x=theme['count'], y=theme['tema'], orientation='h',
                marker=dict(color=theme['count'].values, colorscale='Cividis'),
                text=theme['count'], textposition='outside', textfont=dict(color='white')
            ))
            fig2.update_layout(title='Top 10 Temas de Conteúdo', height=320, **PLOTLY_BASE)
            plotly_axes(fig2)
            st.plotly_chart(fig2, use_container_width=True)

    section_title('Distribuição de Tempo por Secção', NEON_CYAN)
    time_cols = [c for c in ['time_on_feed_per_day','time_on_reels_per_day',
                             'time_on_explore_per_day','time_on_messages_per_day'] if c in df.columns]
    if time_cols:
        time_means = df[time_cols].mean()
        labels = [c.replace('time_on_','').replace('_per_day','').title() for c in time_cols]
        fig3 = px.pie(values=time_means.values, names=labels,
                      title='Tempo Médio por Secção do Instagram',
                      color_discrete_sequence=INSTA_COLORS,
                      template='plotly_dark', hole=0.4)
        fig3.update_layout(**PLOTLY_BASE)
        st.plotly_chart(fig3, use_container_width=True)
        clinical_note(f'Os Reels representam {time_means["time_on_reels_per_day"]/time_means.sum()*100:.1f}% '
                       f'do tempo total — o formato dominante e com maior correlação com stress.', NEON_CYAN)

# Tab 3 — Mercados
with tab3:
    section_title('Performance por Mercado', NEON_CYAN)
    if 'country' in df.columns:
        metrica = st.selectbox('Métrica:', [c for c in [
            'user_engagement_score','daily_active_minutes_instagram',
            'followers_count','posts_created_per_week','digital_addiction_score'
        ] if c in df.columns])

        country_stats = df.groupby('country').agg(
            valor=(metrica,'mean'), n=('user_engagement_score','count')
        ).reset_index().sort_values('valor', ascending=False)

        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure(go.Bar(
                x=country_stats['valor'], y=country_stats['country'],
                orientation='h',
                marker=dict(color=country_stats['valor'].values, colorscale='Viridis'),
                text=country_stats['valor'].round(1), textposition='outside',
                textfont=dict(color='white')
            ))
            fig.update_layout(title=f'{metrica.replace("_"," ").title()} por País',
                              height=380, **{**PLOTLY_BASE, 'margin': dict(l=120,r=60,t=50,b=40)})
            plotly_axes(fig)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = go.Figure(go.Bar(
                x=country_stats['n'], y=country_stats['country'],
                orientation='h',
                marker=dict(color=country_stats['n'].values, colorscale='Purples'),
                text=country_stats['n'].apply(lambda x: f'{x:,}'), textposition='outside',
                textfont=dict(color='white')
            ))
            fig2.update_layout(title='Nº de Utilizadores por País',
                               height=380, **{**PLOTLY_BASE, 'margin': dict(l=120,r=60,t=50,b=40)})
            plotly_axes(fig2)
            st.plotly_chart(fig2, use_container_width=True)

        # Heatmap mercado × persona
        if 'user_persona' in df.columns:
            section_title('Mercado × Persona', NEON_CYAN)
            pivot = df.groupby(['country','user_persona'])['user_engagement_score'].mean().unstack().fillna(0)
            fig3 = go.Figure(go.Heatmap(
                z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                colorscale='Viridis',
                text=pivot.round(2).values, texttemplate='%{text:.1f}',
                textfont=dict(size=9),
                hovertemplate='%{y} — %{x}<br>Engagement: %{z:.2f}<extra></extra>'
            ))
            fig3.update_layout(title='Engagement Score Médio por País × Persona',
                               height=400, **{**PLOTLY_BASE, 'margin': dict(l=100,r=20,t=50,b=80)})
            fig3.update_xaxes(tickangle=-20)
            st.plotly_chart(fig3, use_container_width=True)

# Tab 4 — Premium
with tab4:
    section_title('Análise Premium vs Free', NEON_CYAN)
    if 'subscription_status' in df.columns:
        col1, col2 = st.columns(2)
        sub_counts = df['subscription_status'].value_counts().reset_index()
        sub_counts.columns = ['status','count']

        with col1:
            fig = px.pie(sub_counts, names='status', values='count',
                         title='Distribuição Free vs Premium',
                         color_discrete_sequence=INSTA_COLORS,
                         template='plotly_dark', hole=0.45)
            fig.update_layout(**PLOTLY_BASE)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            metricas_sub = df.groupby('subscription_status').agg(
                engagement=('user_engagement_score','mean'),
                minutos=('daily_active_minutes_instagram','mean'),
                seguidores=('followers_count','mean'),
                posts=('posts_created_per_week','mean')
            ).round(2)
            st.dataframe(metricas_sub, use_container_width=True)

        # Engagement por subscrição e persona
        eng_sub = df.groupby(['subscription_status','user_persona'])['user_engagement_score'].mean().reset_index()
        fig2 = px.bar(eng_sub, x='user_persona', y='user_engagement_score',
                      color='subscription_status',
                      barmode='group', color_discrete_sequence=INSTA_COLORS,
                      title='Engagement por Persona e Tipo de Subscrição',
                      template='plotly_dark')
        fig2.update_layout(**PLOTLY_BASE, height=380)
        plotly_axes(fig2)
        st.plotly_chart(fig2, use_container_width=True)

        clinical_note('Os utilizadores Premium tendem a ter maior engagement e mais seguidores. '
                      'Focar campanhas nos Influencers/Creators Premium maximiza o ROI.', NEON_CYAN)

st.html(f"<p style='color:#1a1a2e; font-size:0.8em; text-align:center; margin-top:3rem;'>📊 Dashboard Marketing · LAD 2025/26</p>")