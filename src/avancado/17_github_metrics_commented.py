# =============================================================================
# 17_github_metrics_commented.py
# Dashboard de métricas GitHub — Sistema de controle de evolução CCNP
#
# Este script é o orquestrador final do pipeline de métricas GitHub.
# Ele conecta dois repositórios e demonstra evolução contínua de estudos.
#
# Pipeline completo:
#   github_api.py   → coleta dados brutos via API → data/raw/
#   processor.py    → transforma JSON em CSVs     → data/processed/
#   este script     → lê CSVs → gera dashboard    → docs/17_github_metrics.html
#
# Estratégia inteligente no main():
#   Se os CSVs já existem → carrega direto (evita chamada à API)
#   Se não existem        → executa coleta + processamento completo
#   Isso permite rodar o dashboard offline após a primeira coleta
#
# 4 abas do dashboard:
#   Aba 1 — Visão Geral   : commits sobrepostos dos dois repos
#   Aba 2 — DASHBOARDS    : tipos, escopos e heatmap de atividade
#   Aba 3 — CISCO         : histórico completo + mensal + heatmap
#   Aba 4 — Correlação    : barras sobrepostas + curvas acumuladas
#
# Narrativa de portfólio:
#   "Commits constantes no CISCO (teoria) + DASHBOARDS (automação) em paralelo
#    demonstram metodologia consistente — não um burst de estudo antes da prova."
# =============================================================================

import os
import sys
import json

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# BASE_DIR: sobe 3 níveis a partir de src/avancado/
#   src/avancado/ → (1) src/ → (2) DASHBOARDS/ (raiz)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

# Importa os módulos do pipeline — responsabilidades separadas
from scripts.collectors.github_api    import collect_all    # coleta API
from scripts.parsing.github.processor import process_all    # processamento

OUTPUT_HTML = os.path.join(BASE_DIR, "docs", "17_github_metrics.html")

# Tema visual consistente com scripts 13-16
BG_COLOR    = "#0F1117"
GRID_COLOR  = "#1E2130"
TEXT_COLOR  = "#E2E8F0"
ACCENT      = "#00C896"
BLUE        = "#4B9EFF"
ORANGE      = "#FB923C"
FONT_FAMILY = "Courier New, monospace"

# Cores dos repositórios — usadas consistentemente em todas as abas
COLOR_DASH  = ACCENT  # verde para DASHBOARDS
COLOR_CISCO = BLUE    # azul para CISCO

# Cores por tipo de commit (Conventional Commits)
TYPE_COLORS = {
    "feat":     "#00C896", "fix":  "#FF4B4B", "docs":     "#4B9EFF",
    "refactor": "#A78BFA", "chore":"#94A3B8", "style":    "#FACC15",
    "test":     "#FB923C", "perf": "#34D399", "ci":       "#60A5FA",
    "build":    "#F472B6", "outro":"#475569",
}

WEEKDAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
WEEKDAY_PT    = ["Seg","Ter","Qua","Qui","Sex","Sab","Dom"]


# =============================================================================
# HELPERS — funções utilitárias reutilizadas em todas as abas
# =============================================================================

def _card(value, label, color=None):
    # Gera HTML de um card de métrica — display:flex no container pai
    # color ou ACCENT como fallback — mantém consistência visual
    c = color or ACCENT
    return f"""<div style="flex:1;min-width:150px;background:#1E2130;border:1px solid {c};
        border-radius:8px;padding:16px;text-align:center;">
        <div style="font-size:28px;font-weight:bold;color:{c};">{value}</div>
        <div style="font-size:12px;color:#94A3B8;">{label}</div></div>"""


def _layout(fig, height=420):
    # Aplica tema escuro padrão em qualquer figura
    # Centralizar aqui evita repetir 8 linhas em cada função de aba
    fig.update_layout(
        paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=height, margin=dict(t=50, b=40, l=10, r=10),
        legend=dict(bgcolor=BG_COLOR, bordercolor=GRID_COLOR, borderwidth=1),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)


# =============================================================================
# ABA 1 — VISÃO GERAL
# Mostra os dois repositórios sobrepostos em uma única linha do tempo
# Objetivo: evidenciar que teoria (CISCO) e prática (DASHBOARDS) evoluem juntos
# =============================================================================

def build_aba_visao_geral(df_dash, df_cisco, repo_info):
    d = repo_info["dashboards"]
    c = repo_info["cisco"]

    cards = f"""<div style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;">
        {_card(len(df_dash),              "Commits DASHBOARDS",  COLOR_DASH)}
        {_card(len(df_cisco),             "Commits CISCO",       COLOR_CISCO)}
        {_card(df_dash['week'].nunique(), "Semanas DASHBOARDS",  COLOR_DASH)}
        {_card(df_cisco['week'].nunique(),"Semanas CISCO",       COLOR_CISCO)}
        {_card(c.get('stars', 0),         "Stars CISCO",         ORANGE)}
    </div>"""

    # Agrupa por semana para comparar frequência de atividade
    cwk_dash  = df_dash.groupby("week").size().reset_index(name="count").sort_values("week")
    cwk_cisco = df_cisco.groupby("week").size().reset_index(name="count").sort_values("week")

    fig = go.Figure()
    # Dois Scatter sobrepostos — fill="tozeroy" cria área preenchida
    # opacity baixa no fill para não bloquear a visualização da sobreposição
    fig.add_trace(go.Scatter(
        x=cwk_dash["week"], y=cwk_dash["count"], name="DASHBOARDS",
        mode="lines+markers", line=dict(color=COLOR_DASH, width=2),
        fill="tozeroy", fillcolor="rgba(0,200,150,0.08)",
        hovertemplate="Semana: %{x}<br>Commits: %{y}<extra>DASHBOARDS</extra>"))
    fig.add_trace(go.Scatter(
        x=cwk_cisco["week"], y=cwk_cisco["count"], name="CISCO",
        mode="lines+markers", line=dict(color=COLOR_CISCO, width=2),
        fill="tozeroy", fillcolor="rgba(75,158,255,0.08)",
        hovertemplate="Semana: %{x}<br>Commits: %{y}<extra>CISCO</extra>"))
    fig.update_layout(title="Commits por semana — os dois repositórios")
    _layout(fig, height=380)

    return cards + pio.to_html(fig, full_html=False, include_plotlyjs=False)


# =============================================================================
# ABA 2 — DASHBOARDS
# Foco na qualidade dos commits: tipos (feat/docs/refactor) e escopos
# Conventional Commits tornam visível o que foi feito em cada semana
# =============================================================================

def build_aba_dashboards(df_dash):
    first  = pd.to_datetime(df_dash["date"]).min().strftime("%d/%m/%Y")
    last   = pd.to_datetime(df_dash["date"]).max().strftime("%d/%m/%Y")
    streak = df_dash["week"].nunique()

    cards = f"""<div style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;">
        {_card(len(df_dash), "Total de Commits", COLOR_DASH)}
        {_card(streak,       "Semanas Ativas",   COLOR_DASH)}
        {_card(first,        "Primeiro Commit",  COLOR_DASH)}
        {_card(last,         "Último Commit",    COLOR_DASH)}
    </div>"""

    # Subplots lado a lado: tipos à esquerda, escopos à direita
    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Commits por tipo", "Commits por escopo (top 10)"),
        horizontal_spacing=0.12)

    type_counts = df_dash["type"].value_counts()
    fig.add_trace(go.Bar(
        x=type_counts.index.tolist(), y=type_counts.values.tolist(),
        # list comprehension aplica cor por tipo — fallback "#475569" para desconhecidos
        marker_color=[TYPE_COLORS.get(t, "#475569") for t in type_counts.index],
        hovertemplate="Tipo: %{x}<br>Commits: %{y}<extra></extra>"),
        row=1, col=1)

    # .head(10) limita aos 10 escopos mais frequentes — evita gráfico poluído
    scope_counts = df_dash["scope"].value_counts().head(10)
    fig.add_trace(go.Bar(
        x=scope_counts.values.tolist(), y=scope_counts.index.tolist(),
        orientation="h", marker_color=COLOR_DASH,
        hovertemplate="Escopo: %{y}<br>Commits: %{x}<extra></extra>"),
        row=1, col=2)

    _layout(fig)

    # Heatmap de atividade — mesmo padrão dos scripts anteriores
    hp = df_dash.groupby(["week","weekday"]).size().unstack(fill_value=0)
    hp = hp.reindex(columns=WEEKDAY_ORDER, fill_value=0)
    hp = hp.loc[sorted(hp.index)]

    fig2 = go.Figure(go.Heatmap(
        z=hp.values.T.tolist(), x=hp.index.tolist(), y=WEEKDAY_PT,
        colorscale=[[0,"#0F1117"],[0.01,"#1a2744"],[0.5,"#1d4ed8"],[1.0,ACCENT]],
        showscale=True,
        colorbar=dict(title=dict(text="commits", font=dict(color=TEXT_COLOR)),
                      tickfont=dict(color=TEXT_COLOR)),
        hovertemplate="Semana: %{x}<br>Dia: %{y}<br>Commits: %{z}<extra></extra>"))
    fig2.update_layout(title="Heatmap de atividade — DASHBOARDS")
    _layout(fig2, height=300)

    return (cards
        + pio.to_html(fig,  full_html=False, include_plotlyjs=False)
        + pio.to_html(fig2, full_html=False, include_plotlyjs=False))


# =============================================================================
# ABA 3 — CISCO
# Foco no volume e consistência: 2369 commits ao longo de 63 semanas
# Mostra que o estudo CCNP é sistemático e contínuo — não um sprint
# =============================================================================

def build_aba_cisco(df_cisco):
    first   = pd.to_datetime(df_cisco["date"]).min().strftime("%d/%m/%Y")
    last    = pd.to_datetime(df_cisco["date"]).max().strftime("%d/%m/%Y")
    semanas = df_cisco["week"].nunique()
    meses   = df_cisco["month"].nunique()

    cards = f"""<div style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;">
        {_card(len(df_cisco), "Total de Commits", COLOR_CISCO)}
        {_card(semanas,       "Semanas Ativas",   COLOR_CISCO)}
        {_card(meses,         "Meses Ativos",     COLOR_CISCO)}
        {_card(first,         "Início",           COLOR_CISCO)}
        {_card(last,          "Último Commit",    COLOR_CISCO)}
    </div>"""

    # Linha semanal — mostra ritmo de trabalho ao longo de 63 semanas
    cwk = df_cisco.groupby("week").size().reset_index(name="count").sort_values("week")
    fig = go.Figure(go.Scatter(
        x=cwk["week"], y=cwk["count"], mode="lines+markers",
        line=dict(color=COLOR_CISCO, width=2), marker=dict(size=4, color=COLOR_CISCO),
        fill="tozeroy", fillcolor="rgba(75,158,255,0.08)",
        hovertemplate="Semana: %{x}<br>Commits: %{y}<extra></extra>"))
    fig.update_layout(title="Evolução de commits — CISCO (histórico completo)")
    _layout(fig, height=320)

    # Barras mensais — granularidade maior para ver padrões sazonais
    cmo = df_cisco.groupby("month").size().reset_index(name="count").sort_values("month")
    fig2 = go.Figure(go.Bar(
        x=cmo["month"], y=cmo["count"], marker_color=COLOR_CISCO,
        hovertemplate="Mês: %{x}<br>Commits: %{y}<extra></extra>"))
    fig2.update_layout(title="Commits por mês — CISCO")
    _layout(fig2, height=320)

    # Heatmap — padrão de dias da semana mais ativos
    hp = df_cisco.groupby(["week","weekday"]).size().unstack(fill_value=0)
    hp = hp.reindex(columns=WEEKDAY_ORDER, fill_value=0)
    hp = hp.loc[sorted(hp.index)]
    fig3 = go.Figure(go.Heatmap(
        z=hp.values.T.tolist(), x=hp.index.tolist(), y=WEEKDAY_PT,
        colorscale=[[0,"#0F1117"],[0.01,"#1a2744"],[0.5,"#1d4ed8"],[1.0,BLUE]],
        showscale=True,
        colorbar=dict(title=dict(text="commits", font=dict(color=TEXT_COLOR)),
                      tickfont=dict(color=TEXT_COLOR)),
        hovertemplate="Semana: %{x}<br>Dia: %{y}<br>Commits: %{z}<extra></extra>"))
    fig3.update_layout(title="Heatmap de atividade — CISCO")
    _layout(fig3, height=350)

    return (cards
        + pio.to_html(fig,  full_html=False, include_plotlyjs=False)
        + pio.to_html(fig2, full_html=False, include_plotlyjs=False)
        + pio.to_html(fig3, full_html=False, include_plotlyjs=False))


# =============================================================================
# ABA 4 — CORRELAÇÃO
# O gráfico mais importante do dashboard para narrativa de portfólio
# Barras sobrepostas mostram semanas com atividade simultânea nos dois repos
# Curvas acumuladas mostram crescimento contínuo ao longo do tempo
# =============================================================================

def build_aba_correlacao(df_all):
    df_dash  = df_all[df_all["repo"] == "dashboards"]
    df_cisco = df_all[df_all["repo"] == "cisco"]

    cwk_dash  = df_dash.groupby("week").size().reset_index(name="count")
    cwk_cisco = df_cisco.groupby("week").size().reset_index(name="count")

    # União de todas as semanas dos dois repositórios
    # Semanas sem atividade em um repo ficam com valor 0 via .get()
    all_weeks  = sorted(set(cwk_dash["week"]) | set(cwk_cisco["week"]))
    dash_map   = dict(zip(cwk_dash["week"],  cwk_dash["count"]))
    cisco_map  = dict(zip(cwk_cisco["week"], cwk_cisco["count"]))
    dash_vals  = [dash_map.get(w, 0)  for w in all_weeks]
    cisco_vals = [cisco_map.get(w, 0) for w in all_weeks]

    fig = make_subplots(rows=2, cols=1,
        subplot_titles=(
            "Commits por semana — sobreposição dos dois repositórios",
            "Atividade acumulada ao longo do tempo"),
        vertical_spacing=0.18)

    # barmode="overlay" sobrepõe as barras — mostra semanas com atividade dupla
    # opacity=0.7 no CISCO para o DASHBOARDS ficar visível na sobreposição
    fig.add_trace(go.Bar(
        x=all_weeks, y=cisco_vals, name="CISCO",
        marker_color=COLOR_CISCO, opacity=0.7,
        hovertemplate="Semana: %{x}<br>Commits CISCO: %{y}<extra></extra>"),
        row=1, col=1)
    fig.add_trace(go.Bar(
        x=all_weeks, y=dash_vals, name="DASHBOARDS",
        marker_color=COLOR_DASH, opacity=0.9,
        hovertemplate="Semana: %{x}<br>Commits DASH: %{y}<extra></extra>"),
        row=1, col=1)

    # Curvas acumuladas — pd.Series.cumsum() soma progressiva
    # Mostra crescimento total ao longo do tempo — não apenas atividade semanal
    cisco_cum = pd.Series(cisco_vals, index=all_weeks).cumsum()
    dash_cum  = pd.Series(dash_vals,  index=all_weeks).cumsum()

    fig.add_trace(go.Scatter(
        x=list(cisco_cum.index), y=list(cisco_cum.values), name="CISCO acum.",
        mode="lines", line=dict(color=COLOR_CISCO, width=2),
        hovertemplate="Semana: %{x}<br>Total acumulado: %{y}<extra>CISCO</extra>"),
        row=2, col=1)
    fig.add_trace(go.Scatter(
        x=list(dash_cum.index), y=list(dash_cum.values), name="DASHBOARDS acum.",
        mode="lines", line=dict(color=COLOR_DASH, width=2),
        hovertemplate="Semana: %{x}<br>Total acumulado: %{y}<extra>DASHBOARDS</extra>"),
        row=2, col=1)

    fig.update_layout(
        barmode="overlay",
        paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=700, margin=dict(t=50, b=40, l=10, r=10),
        legend=dict(bgcolor=BG_COLOR, bordercolor=GRID_COLOR, borderwidth=1))
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    overlap = len(set(cwk_dash["week"]) & set(cwk_cisco["week"]))
    cards = f"""<div style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;">
        {_card(len(df_dash)+len(df_cisco),   "Total de Commits",              ACCENT)}
        {_card(overlap,                       "Semanas com atividade simultânea", ORANGE)}
        {_card(df_dash['week'].nunique(),     "Semanas ativas DASHBOARDS",     COLOR_DASH)}
        {_card(df_cisco['week'].nunique(),    "Semanas ativas CISCO",          COLOR_CISCO)}
    </div>"""

    return cards + pio.to_html(fig, full_html=False, include_plotlyjs=False)


# =============================================================================
# HTML FINAL
# =============================================================================

def build_html(aba1, aba2, aba3, aba4):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GitHub Metrics — CCNP Study System</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0;}}
    body{{background:{BG_COLOR};color:{TEXT_COLOR};font-family:{FONT_FAMILY};padding:24px;}}
    h1{{text-align:center;color:{ACCENT};font-size:22px;margin-bottom:4px;}}
    .subtitle{{text-align:center;color:#94A3B8;font-size:13px;margin-bottom:24px;}}
    .tabs{{display:flex;gap:4px;margin-bottom:20px;border-bottom:2px solid {GRID_COLOR};flex-wrap:wrap;}}
    .tab-btn{{padding:10px 20px;background:{GRID_COLOR};color:#94A3B8;border:none;
      cursor:pointer;font-family:{FONT_FAMILY};font-size:13px;
      border-radius:6px 6px 0 0;transition:all 0.2s;}}
    .tab-btn:hover{{background:#2a3050;color:{TEXT_COLOR};}}
    .tab-btn.active{{background:{BG_COLOR};color:{ACCENT};border:2px solid {ACCENT};
      border-bottom:2px solid {BG_COLOR};margin-bottom:-2px;}}
    .tab-content{{display:none;}}
    .tab-content.active{{display:block;}}
  </style>
</head>
<body>
  <h1>GitHub Metrics — CCNP Study System</h1>
  <p class="subtitle">Evolucao continua — DASHBOARDS + CISCO em paralelo</p>
  <div class="tabs">
    <button class="tab-btn active" onclick="showTab('geral')">Visao Geral</button>
    <button class="tab-btn" onclick="showTab('dashboards')">DASHBOARDS</button>
    <button class="tab-btn" onclick="showTab('cisco')">CISCO</button>
    <button class="tab-btn" onclick="showTab('correlacao')">Correlacao</button>
  </div>
  <div id="geral"      class="tab-content active">{aba1}</div>
  <div id="dashboards" class="tab-content">{aba2}</div>
  <div id="cisco"      class="tab-content">{aba3}</div>
  <div id="correlacao" class="tab-content">{aba4}</div>
  <script>
    function showTab(name){{
      document.querySelectorAll('.tab-content').forEach(el=>el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el=>el.classList.remove('active'));
      document.getElementById(name).classList.add('active');
      event.target.classList.add('active');
    }}
  </script>
</body>
</html>"""


# =============================================================================
# MAIN — Orquestrador inteligente
# Verifica se os CSVs já existem antes de chamar a API
# Permite rodar o dashboard offline após a primeira coleta
# =============================================================================

def main():
    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    csv_all  = os.path.join(processed_dir, "commits_all.csv")
    csv_dash = os.path.join(processed_dir, "commits_dashboards.csv")
    csv_cis  = os.path.join(processed_dir, "commits_cisco.csv")
    json_inf = os.path.join(processed_dir, "repo_info.json")

    # Se todos os arquivos processados existem, carrega direto sem chamar API
    # Isso economiza rate limit do GitHub e torna o dashboard mais rápido
    if all(os.path.exists(p) for p in [csv_all, csv_dash, csv_cis, json_inf]):
        print("[17] Dados ja processados — carregando CSVs...")
        df_all   = pd.read_csv(csv_all,  parse_dates=["date"])
        df_dash  = pd.read_csv(csv_dash, parse_dates=["date"])
        df_cisco = pd.read_csv(csv_cis,  parse_dates=["date"])
        with open(json_inf, encoding="utf-8") as f:
            repo_info = json.load(f)
    else:
        # Primeira execução ou dados desatualizados — executa pipeline completo
        print("[17] Coletando dados da API...")
        raw = collect_all()
        df_dash, df_cisco, df_all = process_all(raw)
        with open(json_inf, encoding="utf-8") as f:
            repo_info = json.load(f)

    print("[17] Gerando dashboard...")
    aba1 = build_aba_visao_geral(df_dash, df_cisco, repo_info)
    aba2 = build_aba_dashboards(df_dash)
    aba3 = build_aba_cisco(df_cisco)
    aba4 = build_aba_correlacao(df_all)

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(build_html(aba1, aba2, aba3, aba4))

    print(f"\n Concluido! Abra: {OUTPUT_HTML}\n")


if __name__ == "__main__":
    main()
