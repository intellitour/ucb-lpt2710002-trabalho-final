"""
Análise de acidentes de trânsito em rodovias federais brasileiras (2017–2023).

Aplicação interativa em Streamlit para exploração visual de dados da PRF,
com gráficos de barras, linhas, pizza, heatmap e mapa georreferenciado.
"""

import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import folium
from folium.plugins import MarkerCluster
import seaborn as sns

# ── Constants ────────────────────────────────────────────────
ORDEM_MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

ORDEM_DIAS = [
    "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
    "sexta-feira", "sábado", "domingo",
]

ORDEM_FASES = ["Amanhecer", "Pleno dia", "Anoitecer", "Plena Noite"]

COLUNAS_EXIBICAO = [
    "data_inversa", "dia_semana", "horario", "uf", "municipio",
    "causa_acidente", "tipo_acidente", "classificacao_acidente",
    "fase_dia", "condicao_metereologica", "tipo_pista", "tracado_via",
    "pessoas", "mortos", "feridos", "veiculos",
]

# ── Matplotlib Configuration ──────────────────────────────────
plt.rcParams.update({
    'figure.figsize': (8, 5),
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 16,
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
})

# ── Helper Functions ──────────────────────────────────────────
def grafico_barras(
    ax, x, y, colors, title, xlabel, ylabel,
    rotation=0, annotate=True, fontsize_annotate=8,
):
    """Cria um gráfico de barras verticais com formatação padronizada.

    Gera barras com borda branca, remove os eixos superior e direito
    e adiciona anotações numéricas sobre cada barra quando solicitado.

    Args:
        ax: Eixo do Matplotlib onde o gráfico será desenhado.
        x: Rótulos do eixo X (categorias).
        y: Valores numéricos para as barras.
        colors: Cores das barras (array ou lista).
        title: Título do gráfico.
        xlabel: Rótulo do eixo X.
        ylabel: Rótulo do eixo Y.
        rotation: Ângulo de rotação dos rótulos do eixo X (em graus).
        annotate: Se True, exibe o valor numérico sobre cada barra.
        fontsize_annotate: Tamanho da fonte das anotações.
    """
    bars = ax.bar(x, y, color=colors, edgecolor='white', linewidth=0.5)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.tick_params(axis='x', rotation=rotation)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if annotate:
        for bar, count in zip(bars, y):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(y) * 0.01,
                f'{count:,}', ha='center', va='bottom',
                fontsize=fontsize_annotate, fontweight='bold',
            )

def grafico_linha(
    ax, x, y, color, title, xlabel, ylabel,
    marker='o', grid=True, annotate=False,
):
    ax.plot(x, y, marker=marker, linewidth=2.5, color=color,
            markersize=8, markeredgecolor='white', markeredgewidth=1.5)
    ax.fill_between(x, y, alpha=0.15, color=color)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if grid:
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    if annotate:
        for xi, yi in zip(x, y):
            ax.annotate(f'{int(yi):,}', xy=(xi, yi), xytext=(0, 8),
                        textcoords="offset points", ha='center',
                        fontsize=8, fontweight='bold')

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Acidentes de trânsito em rodovias",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Data Loading ─────────────────────────────────────────────
@st.cache_data(persist=True)
def carregar_dados() -> pd.DataFrame:
    csv_path = "accidents_2017_to_2023_portugues.csv"
    if not os.path.exists(csv_path):
        st.error(f"Arquivo de dados não encontrado: {csv_path}")
        st.stop()

    df = pd.read_csv(csv_path)

    # Conversão de tipos temporais
    df["data_inversa"] = pd.to_datetime(df["data_inversa"])
    df["ano"] = df["data_inversa"].dt.year
    df["mes"] = df["data_inversa"].dt.month_name("pt_BR")
    df["horario"] = pd.to_datetime(df["horario"], format="%H:%M:%S").dt.hour

    # Tratamento de espaços em colunas numéricas
    for col in ["mortos", "feridos_leves", "feridos_graves", "ilesos",
                "ignorados", "feridos", "pessoas", "veiculos"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.strip(), errors="coerce").fillna(0).astype(int)

    # Remoção de duplicatas
    df = df.drop_duplicates()

    return df

df = carregar_dados()

# ── Sidebar Filters ──────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filtros")

    uf_sel = st.multiselect(
        "Estado (UF)",
        options=sorted(df["uf"].unique()),
        default=sorted(df["uf"].unique()),
    )

    ano_sel = st.multiselect(
        "Ano",
        options=sorted(df["ano"].unique(), reverse=True),
        default=sorted(df["ano"].unique(), reverse=True),
    )

    tipo_acidente_sel = st.multiselect(
        "Tipo de Acidente",
        options=df["tipo_acidente"].unique(),
        default=[],
    )

    causa_sel = st.multiselect(
        "Causa do Acidente",
        options=sorted(df["causa_acidente"].unique()),
        default=[],
    )

    condicao_met_sel = st.multiselect(
        "Condição Meteorológica",
        options=sorted(df["condicao_metereologica"].unique()),
        default=[],
    )

    fase_dia_sel = st.multiselect(
        "Fase do Dia",
        options=ORDEM_FASES,
        default=[],
    )

    st.divider()
    if st.button("Limpar Filtros"):
        st.rerun()

    st.divider()
    st.caption("Dados abertos da PRF - https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf")
    st.caption("Compilados no Kaggle - https://www.kaggle.com/datasets/mlippo/car-accidents-in-brazil-2017-2023")

# ── Apply Filters ────────────────────────────────────────────
mask = (
        (df["uf"].isin(uf_sel))
        & (df["ano"].isin(ano_sel))
        & (df["tipo_acidente"].isin(tipo_acidente_sel) if tipo_acidente_sel else True)
        & (df["causa_acidente"].isin(causa_sel) if causa_sel else True)
        & (df["condicao_metereologica"].isin(condicao_met_sel) if condicao_met_sel else True)
        & (df["fase_dia"].isin(fase_dia_sel) if fase_dia_sel else True)
)
df_filtered = df[mask].copy()

# ── Empty state ──────────────────────────────────────────────
if len(df_filtered) == 0:
    st.info("Nenhum registro encontrado com os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

# ── Summary Metrics ──────────────────────────────────────────
st.title("🚗 Acidentes de Trânsito em Rodovias")
st.subheader("Aluno: Pedro Henrique Ferreira Figueiredo - 2000064523")
st.caption(f"Mostrando {len(df_filtered):,} registros filtrados de {len(df):,} total")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total de Acidentes", f"{len(df_filtered):,}")
c2.metric("Total de Vítimas Fatais", f"{df_filtered['mortos'].sum():,}")
c3.metric("Total de Feridos", f"{df_filtered['feridos'].sum():,}")
c4.metric("Estados Cobertos", f"{df_filtered['uf'].nunique()}")
c5.metric(
    "Taxa de Letalidade",
    f"{df_filtered['mortos'].sum() / len(df_filtered) * 100:.1f}%",
)

st.divider()

# ── Center Tabs ──────────────────────────────────────────────
tab_acidentes, tab_espacial, tab_temporal, tab_dados = st.tabs([
    "📊 Acidentes",
    "🗺️ Análise Espacial",
    "📈 Análise Temporal",
    "📋 Dados Detalhados",
])

# ── Tab 1: Accident Analysis ─────────────────────────────────
with tab_acidentes:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Classificação por Vítimas")
        st.caption("Distribuição dos acidentes conforme o número de vítimas envolvidas")
        df_ac_type = (
            df_filtered["classificacao_acidente"]
            .value_counts()
            .reset_index(name="count")
        )
        df_ac_type = df_ac_type.sort_values("count")
        fig_ac, ax_ac = plt.subplots(figsize=(8, 4))
        colors_ac = plt.cm.Reds(np.linspace(0.4, 1.0, len(df_ac_type)))
        grafico_barras(
            ax_ac, df_ac_type["classificacao_acidente"], df_ac_type["count"],
            colors_ac, "Classificação por Vítimas",
            "Classificação do Acidente", "Número de Acidentes",
            rotation=30, fontsize_annotate=9,
        )
        st.pyplot(fig_ac, width='stretch')

    with col_right:
        st.subheader("Top Causas de Acidentes")
        st.caption("As dez principais causas registradas nos acidentes filtrados")
        df_cause = (
            df_filtered["causa_acidente"]
            .value_counts()
            .head(10)
            .reset_index(name="count")
        )
        fig_cause, ax_cause = plt.subplots(figsize=(8, 4))
        colors_cause = plt.cm.viridis(np.linspace(0, 1, len(df_cause)))
        bars_cause = ax_cause.barh(df_cause["causa_acidente"], df_cause["count"],
                                   color=colors_cause, edgecolor='white', linewidth=0.5)
        ax_cause.set_xlabel("Número de Acidentes", fontsize=11)
        ax_cause.set_ylabel("Causa do Acidente", fontsize=11)
        ax_cause.set_title("Top 10 Causas de Acidentes", fontsize=14, fontweight='bold', pad=15)
        ax_cause.spines['top'].set_visible(False)
        ax_cause.spines['right'].set_visible(False)
        for bar, count in zip(bars_cause, df_cause["count"]):
            ax_cause.text(bar.get_width() + max(df_cause["count"]) * 0.01,
                          bar.get_y() + bar.get_height() / 2,
                          f'{count:,}', ha='left', va='center',
                          fontsize=9, fontweight='bold')
        st.pyplot(fig_cause, width='stretch')

    col_b, col_c = st.columns(2)

    with col_b:
        st.subheader("Acidentes por Estado")
        st.caption("Comparativo do volume de acidentes entre os estados brasileiros")
        df_uf = (
            df_filtered["uf"]
            .value_counts()
            .reset_index(name="count")
        )
        df_uf = df_uf.sort_values("count", ascending=False)
        fig_uf, ax_uf = plt.subplots(figsize=(8, 3.5))
        colors_uf = plt.cm.Blues(np.linspace(0.4, 1.0, len(df_uf)))
        grafico_barras(
            ax_uf, df_uf["uf"], df_uf["count"], colors_uf,
            "Acidentes por Estado", "Estado (UF)", "Número de Acidentes",
            rotation=45,
        )
        st.pyplot(fig_uf, width='stretch')

    with col_c:
        st.subheader("Taxa de Letalidade por Estado")
        st.caption("Percentual de acidentes com vítimas fatais em cada estado")
        df_uf_fatal = (
            df_filtered.groupby("uf").agg(
                total=("mortos", "count"),
                mortos=("mortos", "sum"),
            )
            .reset_index()
            .query("mortos > 0")
        )
        df_uf_fatal["letalidade_pct"] = (
            df_uf_fatal["mortos"] / df_uf_fatal["total"] * 100
        ).round(2)
        df_uf_fatal = df_uf_fatal.sort_values("letalidade_pct", ascending=False)
        fig_uf_fatal, ax_uf_fatal = plt.subplots(figsize=(8, 3.5))
        colors_uf_fatal = plt.cm.RdYlGn_r(np.linspace(0.3, 1.0, len(df_uf_fatal)))
        bars_uf_fatal = ax_uf_fatal.bar(
            df_uf_fatal["uf"], df_uf_fatal["letalidade_pct"],
            color=colors_uf_fatal, edgecolor='white', linewidth=0.5,
        )
        ax_uf_fatal.set_xlabel("Estado (UF)", fontsize=11)
        ax_uf_fatal.set_ylabel("Taxa de Letalidade (%)", fontsize=11)
        ax_uf_fatal.set_title("Taxa de Letalidade por Estado", fontsize=14, fontweight='bold', pad=15)
        ax_uf_fatal.tick_params(axis='x', rotation=45)
        ax_uf_fatal.spines['top'].set_visible(False)
        ax_uf_fatal.spines['right'].set_visible(False)
        for bar, pct in zip(bars_uf_fatal, df_uf_fatal["letalidade_pct"]):
            ax_uf_fatal.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(df_uf_fatal["letalidade_pct"]) * 0.01,
                f'{pct:.1f}%', ha='center', va='bottom',
                fontsize=7, fontweight='bold',
            )
        st.pyplot(fig_uf_fatal, width='stretch')

    col_d, col_e = st.columns(2)

    with col_d:
        st.subheader("Acidentes por Tipo")
        st.caption("Proporção dos diferentes tipos de acidentes registrados")
        df_tipo = (
            df_filtered["tipo_acidente"]
            .value_counts()
            .head(8)
            .reset_index(name="count")
        )
        fig_tipo, ax_tipo = plt.subplots(figsize=(6, 5))
        colors_tipo = plt.cm.Set3(np.linspace(0, 1, len(df_tipo)))
        wedges, texts, autotexts = ax_tipo.pie(
            df_tipo["count"],
            labels=df_tipo["tipo_acidente"],
            autopct='%1.1f%%',
            colors=colors_tipo,
            startangle=90,
            pctdistance=0.85,
            wedgeprops=dict(edgecolor='white', linewidth=1.5),
        )
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        ax_tipo.set_title("Distribuição por Tipo de Acidente", fontsize=14, fontweight='bold', pad=15)
        ax_tipo.legend(wedges, df_tipo["tipo_acidente"], title="Tipos",
                       loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
        st.pyplot(fig_tipo, width='stretch')

    with col_e:
        st.subheader("Acidentes por Tipo de Pista")
        st.caption("Comparativo entre pistas simples e duplas")
        df_pista = (
            df_filtered["tipo_pista"]
            .value_counts()
            .reset_index(name="count")
        )
        fig_pista, ax_pista = plt.subplots(figsize=(8, 3.5))
        colors_pista = plt.cm.Greens(np.linspace(0.4, 1.0, len(df_pista)))
        grafico_barras(
            ax_pista, df_pista["tipo_pista"], df_pista["count"], colors_pista,
            "Acidentes por Tipo de Pista", "Tipo de Pista", "Número de Acidentes",
            rotation=30,
        )
        st.pyplot(fig_pista, width='stretch')

    col_f, col_g = st.columns(2)

    with col_f:
        st.subheader("Acidentes por Traçado da Via")
        st.caption("Impacto do traçado (reta vs curva) na ocorrência de acidentes")
        df_tracado = (
            df_filtered["tracado_via"]
            .value_counts()
            .reset_index(name="count")
        )
        fig_tracado, ax_tracado = plt.subplots(figsize=(8, 3.5))
        colors_tracado = plt.cm.PuBu(np.linspace(0.4, 1.0, len(df_tracado)))
        grafico_barras(
            ax_tracado, df_tracado["tracado_via"], df_tracado["count"], colors_tracado,
            "Acidentes por Traçado da Via", "Traçado da Via", "Número de Acidentes",
            rotation=30,
        )
        st.pyplot(fig_tracado, width='stretch')

    with col_g:
        st.subheader("Top 15 Rodovias (BR) Mais Perigosas")
        st.caption("Rodovias federais com maior número de mortes registradas")
        df_br = (
            df_filtered.groupby("br").agg(
                acidentes=("mortos", "count"),
                mortos=("mortos", "sum"),
            )
            .reset_index()
            .dropna(subset=["br"])
            .sort_values("mortos", ascending=False)
            .head(15)
        )
        fig_br, ax_br = plt.subplots(figsize=(8, 4))
        colors_br = plt.cm.YlOrRd(np.linspace(0.4, 1.0, len(df_br)))
        bars_br = ax_br.barh(
            [f"BR-{int(b):03d}" for b in df_br["br"]],
            df_br["mortos"], color=colors_br, edgecolor='white', linewidth=0.5,
        )
        ax_br.set_xlabel("Número de Mortos", fontsize=11)
        ax_br.set_ylabel("Rodovia Federal", fontsize=11)
        ax_br.set_title("Top 15 Rodovias por Mortes", fontsize=14, fontweight='bold', pad=15)
        ax_br.spines['top'].set_visible(False)
        ax_br.spines['right'].set_visible(False)
        for bar, count in zip(bars_br, df_br["mortos"]):
            ax_br.text(bar.get_width() + max(df_br["mortos"]) * 0.01,
                       bar.get_y() + bar.get_height() / 2,
                       f'{int(count):,}', ha='left', va='center',
                       fontsize=9, fontweight='bold')
        st.pyplot(fig_br, width='stretch')

# ── Tab 2: Spatial Analysis ──────────────────────────────────
with tab_espacial:
    col_map1, col_map2 = st.columns(2)

    with col_map1:
        st.subheader("Distribuição Geográfica dos Acidentes")
        st.caption("Mapa interativo mostrando a localização dos acidentes no território brasileiro")

        color_map = {
            "Com Vítimas Fatais": "red",
            "Sem Vítimas": "green",
            "Com Vítimas Feridas": "orange",
        }

        df_map = df_filtered.copy()
        if len(df_map) > 2000:
            df_map = df_map.sample(n=2000, random_state=42)

        m = folium.Map(
            location=[-14.235, -51.9253],
            zoom_start=4,
            tiles="OpenStreetMap",
        )

        cluster = MarkerCluster().add_to(m)
        for _, row in df_map.iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=max(2, np.sqrt(row["pessoas"]) * 2),
                color=color_map.get(row["classificacao_acidente"], "gray"),
                fill=True,
                fill_color=color_map.get(row["classificacao_acidente"], "gray"),
                fill_opacity=0.6,
                popup=f"""
                    <b>{row['classificacao_acidente']}</b><br>
                    Município: {row['municipio']}<br>
                    Data: {row['data_inversa'].strftime('%d/%m/%Y')}<br>
                    Pessoas envolvidas: {row['pessoas']}<br>
                    Mortos: {row['mortos']}<br>
                    Feridos: {row['feridos']}
                """,
                tooltip=f"{row['classificacao_acidente']} - {row['municipio']}"
            ).add_to(cluster)

        st.iframe(m._repr_html_(), height=600)

        st.markdown("""
            <div style='display: flex; gap: 15px; margin-top: 10px;'>
                <div style='display: flex; align-items: center; gap: 5px;'>
                    <div style='width: 15px; height: 15px; background-color: red; border-radius: 50%;'></div>
                    <span>Com Vítimas Fatais</span>
                </div>
                <div style='display: flex; align-items: center; gap: 5px;'>
                    <div style='width: 15px; height: 15px; background-color: orange; border-radius: 50%;'></div>
                    <span>Com Vítimas Feridas</span>
                </div>
                <div style='display: flex; align-items: center; gap: 5px;'>
                    <div style='width: 15px; height: 15px; background-color: green; border-radius: 50%;'></div>
                    <span>Sem Vítimas</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_map2:
        st.subheader("Acidentes por Região (Regional)")
        st.caption("Volume de acidentes agrupado pelas regiões administrativas")
        df_regional = (
            df_filtered["regional"]
            .value_counts()
            .head(12)
            .reset_index(name="count")
        )
        fig_reg, ax_reg = plt.subplots(figsize=(8, 4))
        colors_reg = plt.cm.Reds(np.linspace(0.4, 1.0, len(df_regional)))
        grafico_barras(
            ax_reg, df_regional["regional"], df_regional["count"], colors_reg,
            "Top Regiões Administrativas", "Regional", "Número de Acidentes",
            rotation=45,
        )
        st.pyplot(fig_reg, width='stretch')

    col_w1, col_w2 = st.columns(2)

    with col_w1:
        st.subheader("Acidentes por Condição Meteorológica")
        st.caption("Relação entre as condições climáticas e a frequência de acidentes")
        df_weather = (
            df_filtered["condicao_metereologica"]
            .value_counts()
            .reset_index(name="count")
        )
        fig_weather, ax_weather = plt.subplots(figsize=(8, 3.5))
        colors_weather = plt.cm.YlOrRd(np.linspace(0.3, 1.0, len(df_weather)))
        grafico_barras(
            ax_weather, df_weather["condicao_metereologica"], df_weather["count"],
            colors_weather, "Acidentes por Condição Meteorológica",
            "Condição Meteorológica", "Número de Acidentes",
            rotation=30,
        )
        st.pyplot(fig_weather, width='stretch')

    with col_w2:
        st.subheader("Taxa de Letalidade por Condição Meteorológica")
        st.caption("Percentual de mortes em relação ao total de acidentes por condição climática")
        df_weather_fatal = (
            df_filtered.groupby("condicao_metereologica").agg(
                total=("mortos", "count"),
                mortos=("mortos", "sum"),
            )
            .reset_index()
            .query("mortos > 0")
        )
        df_weather_fatal["letalidade_pct"] = (
            df_weather_fatal["mortos"] / df_weather_fatal["total"] * 100
        ).round(2)
        df_weather_fatal = df_weather_fatal.sort_values("letalidade_pct", ascending=False)
        fig_wf, ax_wf = plt.subplots(figsize=(8, 3.5))
        colors_wf = plt.cm.YlOrRd(np.linspace(0.3, 1.0, len(df_weather_fatal)))
        bars_wf = ax_wf.bar(
            df_weather_fatal["condicao_metereologica"],
            df_weather_fatal["letalidade_pct"],
            color=colors_wf, edgecolor='white', linewidth=0.5,
        )
        ax_wf.set_xlabel("Condição Meteorológica", fontsize=11)
        ax_wf.set_ylabel("Taxa de Letalidade (%)", fontsize=11)
        ax_wf.set_title("Letalidade por Condição Climática", fontsize=14, fontweight='bold', pad=15)
        ax_wf.tick_params(axis='x', rotation=30)
        ax_wf.spines['top'].set_visible(False)
        ax_wf.spines['right'].set_visible(False)
        for bar, pct in zip(bars_wf, df_weather_fatal["letalidade_pct"]):
            ax_wf.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(df_weather_fatal["letalidade_pct"]) * 0.01,
                f'{pct:.1f}%', ha='center', va='bottom',
                fontsize=8, fontweight='bold',
            )
        st.pyplot(fig_wf, width='stretch')

# ── Tab 3: Temporal Analysis ─────────────────────────────────
with tab_temporal:
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.subheader("Evolução Temporal (Mensal)")
        st.caption("Comportamento sazonal dos acidentes ao longo dos meses do ano")
        df_monthly = (
            df_filtered.groupby("mes")
            .size()
            .reset_index(name="count")
        )
        df_monthly["mes"] = pd.Categorical(df_monthly["mes"], categories=ORDEM_MESES, ordered=True)
        df_monthly = df_monthly.sort_values("mes")
        fig_monthly, ax_monthly = plt.subplots(figsize=(8, 4))
        grafico_linha(
            ax_monthly, range(len(df_monthly)), df_monthly["count"],
            '#1f77b4', "Evolução Temporal Mensal\n(Agregado nos anos filtrados)",
            "Mês", "Número de Acidentes",
            marker='o', annotate=True,
        )
        ax_monthly.set_xticks(range(len(ORDEM_MESES)))
        ax_monthly.set_xticklabels(ORDEM_MESES, rotation=45, ha='right')
        st.pyplot(fig_monthly, width='stretch')

    with col_t2:
        st.subheader("Acidentes por Ano")
        st.caption("Tendência anual do volume total de acidentes registrados")
        df_yearly = (
            df_filtered.groupby("ano")
            .size()
            .reset_index(name="count")
        )
        fig_yearly, ax_yearly = plt.subplots(figsize=(8, 4))
        colors_yearly = plt.cm.plasma(np.linspace(0.3, 0.9, len(df_yearly)))
        grafico_barras(
            ax_yearly, df_yearly["ano"], df_yearly["count"], colors_yearly,
            "Acidentes por Ano\n(Tendência temporal anual)",
            "Ano", "Número de Acidentes",
        )
        st.pyplot(fig_yearly, width='stretch')

    col_t3, col_t4 = st.columns(2)

    with col_t3:
        st.subheader("Acidentes por Dia da Semana")
        st.caption("Variação semanal dos acidentes — impacto do dia da semana na ocorrência")
        df_weekday = (
            df_filtered["dia_semana"]
            .value_counts()
            .reset_index(name="count")
        )
        df_weekday["dia"] = pd.Categorical(df_weekday["dia_semana"], categories=ORDEM_DIAS, ordered=True)
        fig_weekday, ax_weekday = plt.subplots(figsize=(8, 3.5))
        colors_weekday = plt.cm.YlGn(np.linspace(0.3, 1.0, len(df_weekday)))
        grafico_barras(
            ax_weekday, df_weekday["dia"], df_weekday["count"], colors_weekday,
            "Acidentes por Dia da Semana\n(Variação semanal)",
            "Dia da Semana", "Número de Acidentes",
        )
        st.pyplot(fig_weekday, width='stretch')

    with col_t4:
        st.subheader("Acidentes por Fase do Dia")
        st.caption("Distribuição dos acidentes conforme a fase do dia")
        df_fase = (
            df_filtered["fase_dia"]
            .value_counts()
            #.reindex(ORDEM_FASES, fill_value=0)
            .reset_index(name="count")
        )
        fig_fase, ax_fase = plt.subplots(figsize=(8, 3.5))
        colors_fase = plt.cm.PuOr(np.linspace(0.7, 1.0, len(df_fase)))
        grafico_barras(
            ax_fase, df_fase["fase_dia"], df_fase["count"], colors_fase,
            "Acidentes por Fase do Dia",
            "Fase do Dia", "Número de Acidentes",
            rotation=30,
        )
        st.pyplot(fig_fase, width='stretch')

    col_t5, col_t6 = st.columns(2)

    with col_t5:
        st.subheader("Acidentes por Horário")
        st.caption("Distribuição horária dos acidentes ao longo do dia")
        df_hour = (
            df_filtered.groupby("horario")
            .size()
            .reset_index(name="count")
        )
        fig_hour, ax_hour = plt.subplots(figsize=(8, 3.5))
        grafico_linha(
            ax_hour, df_hour["horario"], df_hour["count"],
            '#d62728', "Acidentes por Horário do Dia\n(Pico de ocorrências)",
            "Horário do Dia", "Número de Acidentes",
            marker='s',
        )
        ax_hour.set_xticks(range(0, 24, 2))
        st.pyplot(fig_hour, width='stretch')

    with col_t6:
        st.subheader("Heatmap: Meses × Anos")
        st.caption("Intensidade de acidentes por mês e ano — identifica sazonalidade e tendências")
        df_heatmap = (
            df_filtered.groupby(["ano", "mes"])
            .size()
            .unstack(fill_value=0)
        )
        df_heatmap = df_heatmap[ORDEM_MESES]
        fig_heat, ax_heat = plt.subplots(figsize=(10, 5))
        sns.heatmap(df_heatmap, annot=True, fmt='d', cmap='YlOrRd', ax=ax_heat,
                    cbar_kws={'label': 'Nº de Acidentes'})
        ax_heat.set_title("Acidentes por Mês e Ano", fontsize=14, fontweight='bold', pad=15)
        ax_heat.set_xlabel("Mês", fontsize=11)
        ax_heat.set_ylabel("Ano", fontsize=11)
        ax_heat.tick_params(axis='x', rotation=45, labelsize=9)
        st.pyplot(fig_heat, width='stretch')

    col_t7, col_t8 = st.columns(2)

    with col_t7:
        st.subheader("Vítimas por Ano (Mortos vs Feridos)")
        st.caption("Comparativo entre vítimas fatais e feridas ao longo dos anos")
        df_victims = (
            df_filtered.groupby("ano")
            .agg(mortos=("mortos", "sum"), feridos=("feridos", "sum"))
            .reset_index()
        )
        fig_victims, ax_victims = plt.subplots(figsize=(8, 4))
        x = np.arange(len(df_victims["ano"]))
        width = 0.35
        bars_mortos = ax_victims.bar(x - width/2, df_victims["mortos"], width,
                                     label="Mortos", color='#d62728',
                                     edgecolor='white', linewidth=0.5)
        bars_feridos = ax_victims.bar(x + width/2, df_victims["feridos"], width,
                                      label="Feridos", color='#ff7f0e',
                                      edgecolor='white', linewidth=0.5)
        ax_victims.set_xlabel("Ano", fontsize=11)
        ax_victims.set_ylabel("Número de Vítimas", fontsize=11)
        ax_victims.set_title("Vítimas por Ano\n(Mortos vs Feridos — comparativo anual)",
                             fontsize=14, fontweight='bold', pad=15)
        ax_victims.set_xticks(x)
        ax_victims.set_xticklabels(df_victims["ano"])
        ax_victims.legend(title="Vítimas", fontsize=10, loc='upper right')
        ax_victims.spines['top'].set_visible(False)
        ax_victims.spines['right'].set_visible(False)
        ax_victims.grid(True, alpha=0.3, linestyle='--', axis='y')
        for bar in bars_mortos:
            h = bar.get_height()
            if h > 0:
                ax_victims.text(bar.get_x() + bar.get_width() / 2,
                                h + max(df_victims["mortos"]) * 0.01,
                                f'{int(h):,}', ha='center', va='bottom',
                                fontsize=8, fontweight='bold', color='#d62728')
        for bar in bars_feridos:
            h = bar.get_height()
            if h > 0:
                ax_victims.text(bar.get_x() + bar.get_width() / 2,
                                h + max(df_victims["feridos"]) * 0.01,
                                f'{int(h):,}', ha='center', va='bottom',
                                fontsize=8, fontweight='bold', color='#ff7f0e')
        st.pyplot(fig_victims, width='stretch')

    with col_t8:
        st.subheader("Top 5 Causas por Ano")
        st.caption("Evolução das principais causas de acidentes ao longo dos anos")
        df_cause_year = (
            df_filtered[df_filtered["causa_acidente"].notna()]
            .groupby(["ano", "causa_acidente"])
            .size()
            .reset_index(name="count")
        )
        top5_causes = (
            df_cause_year.groupby("causa_acidente")["count"]
            .sum()
            .nlargest(5)
            .index
        )
        df_cause_year = df_cause_year[df_cause_year["causa_acidente"].isin(top5_causes)]
        df_pivot = df_cause_year.pivot_table(
            index="ano", columns="causa_acidente", values="count",
            aggfunc="sum", fill_value=0,
        )
        fig_cause_year, ax_cause_year = plt.subplots(figsize=(8, 4))
        df_pivot.plot.bar(stacked=True, ax=ax_cause_year, edgecolor='white', linewidth=0.3)
        ax_cause_year.set_xlabel("Ano", fontsize=11)
        ax_cause_year.set_ylabel("Número de Acidentes", fontsize=11)
        ax_cause_year.set_title("Top 5 Causas por Ano\n(Barras empilhadas)",
                                fontsize=14, fontweight='bold', pad=15)
        ax_cause_year.spines['top'].set_visible(False)
        ax_cause_year.spines['right'].set_visible(False)
        ax_cause_year.legend(title="Causas", fontsize=8, loc='upper right',
                             bbox_to_anchor=(1.25, 1.0))
        ax_cause_year.tick_params(axis='x', rotation=0)
        st.pyplot(fig_cause_year, width='stretch')

# ── Tab 4: Detailed Data ─────────────────────────────────────
with tab_dados:
    st.subheader("Dados Detalhados")

    sort_col = st.selectbox(
        "Ordenar por",
        options=["data_inversa", "mortos", "feridos", "pessoas", "municipio"],
        index=0,
    )
    sort_asc = st.checkbox("Crescente", value=False)

    df_sorted = df_filtered.sort_values(sort_col, ascending=sort_asc)

    search_term = st.text_input("🔍 Buscar por município", placeholder="Digite o nome do município...")
    if search_term:
        df_sorted = df_sorted[df_sorted["municipio"].str.contains(search_term, case=False, na=False)]

    st.dataframe(
        df_sorted[COLUNAS_EXIBICAO],
        width='stretch',
        height=500,
        hide_index=True,
    )

    st.download_button(
        label="📥 Baixar dados filtrados (CSV)",
        data="\ufeff" + df_sorted[COLUNAS_EXIBICAO].to_csv(index=False),
        file_name="acidentes_filtrados.csv",
        mime="text/csv",
    )
