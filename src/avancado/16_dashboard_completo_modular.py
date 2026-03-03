import argparse
import os
import sys

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from scripts.parsing.git_log.extract   import validate_repo, extract_git_log
from scripts.parsing.git_log.parser    import parse_lines, save_csv
from scripts.parsing.blueprint.scanner import scan_blueprint, DOMAIN_ORDER, DOMAIN_COLORS


OUTPUT_CSV  = os.path.join(BASE_DIR, "data", "processed", "git_log.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "docs", "16_dashboard_completo_modular.html")

ACTION_COLORS = {
    "Alterado": "#4B9EFF", "Adicionado": "#00C896", "Ajustado": "#FB923C",
    "Acertado": "#A78BFA", "Removido":   "#FF4B4B", "Realizado": "#FACC15",
    "Separado": "#94A3B8", "Dividido":   "#94A3B8", "Criado":    "#34D399",
    "Corrigido":"#F472B6", "Atualizado": "#60A5FA", "Renomeado": "#CBD5E1",
    "Teste":    "#FCD34D", "Outro":      "#475569",
}

WEEKDAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
WEEKDAY_PT    = ["Seg","Ter","Qua","Qui","Sex","Sab","Dom"]

BG_COLOR    = "#0F1117"
GRID_COLOR  = "#1E2130"
TEXT_COLOR  = "#E2E8F0"
ACCENT      = "#00C896"
FONT_FAMILY = "Courier New, monospace"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dashboard completo CCNP — versao modular com 3 abas.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--repo", required=True, metavar="REPO",
        help="Caminho para a raiz do repositorio Git\nEx: D:\\ESTUDOS\\CISCO\\CISCO")
    parser.add_argument("--ccnp", required=True, metavar="CCNP",
        help="Caminho para a pasta do Blueprint\nEx: D:\\ESTUDOS\\CISCO\\CISCO\\CCNP 350-401 ENCOR")
    return parser.parse_args()


def validate_ccnp(ccnp_path):
    if not os.path.isdir(ccnp_path):
        raise FileNotFoundError(f"Pasta CCNP nao encontrada: {ccnp_path}")


def build_aba_resumo(domains, df):
    total_subtopics    = sum(d["total_subtopics"] for d in domains.values())
    total_labs         = sum(d["total_labs"]      for d in domains.values())
    dominios_iniciados = sum(1 for d in domains.values() if d["total_subtopics"] > 0)
    total_commits      = len(df)

    dom_names  = [d.split(" - ", 1)[1] for d in DOMAIN_ORDER]
    dom_subs   = [domains[d]["total_subtopics"] for d in DOMAIN_ORDER]
    dom_colors = [DOMAIN_COLORS[d] for d in DOMAIN_ORDER]

    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Subtopicos por dominio", "Commits ao longo do tempo"),
        horizontal_spacing=0.12)
    fig.add_trace(go.Bar(x=dom_subs, y=dom_names, orientation="h",
        marker_color=dom_colors,
        hovertemplate="Dominio: %{y}<br>Subtopicos: %{x}<extra></extra>"), row=1, col=1)
    cwk = df.groupby("week").size().reset_index(name="count").sort_values("week")
    fig.add_trace(go.Scatter(x=cwk["week"], y=cwk["count"], mode="lines+markers",
        line=dict(color=ACCENT, width=2), marker=dict(size=5, color=ACCENT),
        fill="tozeroy", fillcolor="rgba(0,200,150,0.1)",
        hovertemplate="Semana: %{x}<br>Commits: %{y}<extra></extra>"), row=1, col=2)
    fig.update_layout(paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=380, showlegend=False, margin=dict(t=50, b=40, l=10, r=10))
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    cards = f"""<div style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;">
      <div style="flex:1;min-width:140px;background:#1E2130;border:1px solid {ACCENT};border-radius:8px;padding:16px;text-align:center;">
        <div style="font-size:28px;font-weight:bold;color:{ACCENT};">{total_commits}</div>
        <div style="font-size:12px;color:#94A3B8;">Total de Commits</div></div>
      <div style="flex:1;min-width:140px;background:#1E2130;border:1px solid {ACCENT};border-radius:8px;padding:16px;text-align:center;">
        <div style="font-size:28px;font-weight:bold;color:{ACCENT};">{total_subtopics}</div>
        <div style="font-size:12px;color:#94A3B8;">Subtopicos Criados</div></div>
      <div style="flex:1;min-width:140px;background:#1E2130;border:1px solid {ACCENT};border-radius:8px;padding:16px;text-align:center;">
        <div style="font-size:28px;font-weight:bold;color:{ACCENT};">{total_labs}</div>
        <div style="font-size:12px;color:#94A3B8;">Labs Realizados</div></div>
      <div style="flex:1;min-width:140px;background:#1E2130;border:1px solid {ACCENT};border-radius:8px;padding:16px;text-align:center;">
        <div style="font-size:28px;font-weight:bold;color:{ACCENT};">{dominios_iniciados}/6</div>
        <div style="font-size:12px;color:#94A3B8;">Dominios Iniciados</div></div>
    </div>"""
    return cards + pio.to_html(fig, full_html=False, include_plotlyjs=False)


def build_aba_progresso(domains):
    dom_names  = [d.split(" - ", 1)[1] for d in DOMAIN_ORDER]
    dom_subs   = [domains[d]["total_subtopics"] for d in DOMAIN_ORDER]
    dom_labs   = [domains[d]["total_labs"]      for d in DOMAIN_ORDER]
    dom_colors = [DOMAIN_COLORS[d]             for d in DOMAIN_ORDER]

    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Subtopicos vs Labs por dominio", "Distribuicao de subtopicos"),
        specs=[[{"type":"xy"},{"type":"domain"}]], horizontal_spacing=0.12)
    fig.add_trace(go.Bar(name="Subtopicos", x=dom_names, y=dom_subs,
        marker_color=dom_colors,
        hovertemplate="Dominio: %{x}<br>Subtopicos: %{y}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Bar(name="Labs", x=dom_names, y=dom_labs,
        marker_color=["rgba(255,75,75,0.8)"]*6,
        hovertemplate="Dominio: %{x}<br>Labs: %{y}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Pie(labels=dom_names, values=dom_subs,
        marker_colors=dom_colors, hole=0.4,
        hovertemplate="Dominio: %{label}<br>Subtopicos: %{value}<br>(%{percent})<extra></extra>"),
        row=1, col=2)
    fig.update_layout(paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY), height=420, barmode="group",
        legend=dict(bgcolor=BG_COLOR, bordercolor=GRID_COLOR, borderwidth=1),
        margin=dict(t=50, b=40, l=10, r=10))
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    rows = ""
    for domain in DOMAIN_ORDER:
        d      = domains[domain]
        name   = domain.split(" - ", 1)[1]
        subs   = d["total_subtopics"]
        labs   = d["total_labs"]
        tops   = len(d["topics"])
        color  = DOMAIN_COLORS[domain]
        status = "Iniciado" if subs > 0 else "Pendente"
        rows += f"""<tr>
          <td style="padding:8px 12px;"><span style="display:inline-block;width:12px;height:12px;
            background:{color};border-radius:50%;margin-right:8px;"></span>{name}</td>
          <td style="padding:8px 12px;text-align:center;">{tops}</td>
          <td style="padding:8px 12px;text-align:center;">{subs}</td>
          <td style="padding:8px 12px;text-align:center;color:#FF4B4B;">{labs}</td>
          <td style="padding:8px 12px;text-align:center;">{status}</td></tr>"""

    table = f"""<table style="width:100%;border-collapse:collapse;margin-top:20px;
        background:#1E2130;border-radius:8px;overflow:hidden;
        font-family:Courier New,monospace;color:{TEXT_COLOR};">
      <thead><tr style="background:#0F1117;border-bottom:1px solid {ACCENT};">
        <th style="padding:10px 12px;text-align:left;">Dominio</th>
        <th style="padding:10px 12px;text-align:center;">Topicos</th>
        <th style="padding:10px 12px;text-align:center;">Subtopicos</th>
        <th style="padding:10px 12px;text-align:center;">Labs</th>
        <th style="padding:10px 12px;text-align:center;">Status</th>
      </tr></thead><tbody>{rows}</tbody></table>"""
    return pio.to_html(fig, full_html=False, include_plotlyjs=False) + table


def build_aba_commits(df):
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=("Commits ao longo do tempo", "Distribuicao por acao",
                        "Distribuicao por dominio", "Heatmap dia vs semana"),
        vertical_spacing=0.18, horizontal_spacing=0.12,
        specs=[[{"type":"xy"},{"type":"xy"}],[{"type":"xy"},{"type":"xy"}]])

    cwk = df.groupby("week").size().reset_index(name="count").sort_values("week")
    fig.add_trace(go.Scatter(x=cwk["week"], y=cwk["count"], mode="lines+markers",
        line=dict(color=ACCENT, width=2), marker=dict(size=5, color=ACCENT),
        fill="tozeroy", fillcolor="rgba(0,200,150,0.1)",
        hovertemplate="Semana: %{x}<br>Commits: %{y}<extra></extra>"), row=1, col=1)

    ac = df["action"].value_counts()
    fig.add_trace(go.Bar(x=ac.index.tolist(), y=ac.values.tolist(),
        marker_color=[ACTION_COLORS.get(a, "#475569") for a in ac.index],
        hovertemplate="Acao: %{x}<br>Commits: %{y}<extra></extra>"), row=1, col=2)

    dc = df["domain"].value_counts()
    fig.add_trace(go.Bar(x=dc.values.tolist(), y=dc.index.tolist(), orientation="h",
        marker_color="#4B9EFF",
        hovertemplate="Dominio: %{y}<br>Commits: %{x}<extra></extra>"), row=2, col=1)

    hp = df.groupby(["week","weekday"]).size().unstack(fill_value=0)
    hp = hp.reindex(columns=WEEKDAY_ORDER, fill_value=0)
    hp = hp.loc[sorted(hp.index)]
    fig.add_trace(go.Heatmap(z=hp.values.T.tolist(), x=hp.index.tolist(), y=WEEKDAY_PT,
        colorscale=[[0.0,"#0F1117"],[0.01,"#1a2744"],[0.3,"#1d4ed8"],[0.6,"#0ea5e9"],[1.0,ACCENT]],
        showscale=True,
        colorbar=dict(title=dict(text="commits", font=dict(color=TEXT_COLOR)),
                      tickfont=dict(color=TEXT_COLOR), x=1.02),
        hovertemplate="Semana: %{x}<br>Dia: %{y}<br>Commits: %{z}<extra></extra>"), row=2, col=2)

    fig.update_layout(paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=700, showlegend=False, margin=dict(t=50, b=40, l=10, r=60))
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    total_commits = len(df)
    total_labs    = (df["lab"] == "Sim").sum()
    first_commit  = df["date"].min().strftime("%d/%m/%Y")
    last_commit   = df["date"].max().strftime("%d/%m/%Y")

    cards = f"""<div style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;">
      <div style="flex:1;min-width:140px;background:#1E2130;border:1px solid {ACCENT};border-radius:8px;padding:16px;text-align:center;">
        <div style="font-size:28px;font-weight:bold;color:{ACCENT};">{total_commits}</div>
        <div style="font-size:12px;color:#94A3B8;">Total de Commits</div></div>
      <div style="flex:1;min-width:140px;background:#1E2130;border:1px solid {ACCENT};border-radius:8px;padding:16px;text-align:center;">
        <div style="font-size:28px;font-weight:bold;color:{ACCENT};">{first_commit}</div>
        <div style="font-size:12px;color:#94A3B8;">Primeiro Commit</div></div>
      <div style="flex:1;min-width:140px;background:#1E2130;border:1px solid {ACCENT};border-radius:8px;padding:16px;text-align:center;">
        <div style="font-size:28px;font-weight:bold;color:{ACCENT};">{last_commit}</div>
        <div style="font-size:12px;color:#94A3B8;">Ultimo Commit</div></div>
      <div style="flex:1;min-width:140px;background:#1E2130;border:1px solid {ACCENT};border-radius:8px;padding:16px;text-align:center;">
        <div style="font-size:28px;font-weight:bold;color:{ACCENT};">{total_labs}</div>
        <div style="font-size:12px;color:#94A3B8;">Labs nos Commits</div></div>
    </div>"""
    return cards + pio.to_html(fig, full_html=False, include_plotlyjs=False)


def build_html(aba1, aba2, aba3):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard CCNP ENCORE 350-401 Modular</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0;}}
    body{{background:{BG_COLOR};color:{TEXT_COLOR};font-family:{FONT_FAMILY};padding:24px;}}
    h1{{text-align:center;color:{ACCENT};font-size:22px;margin-bottom:8px;}}
    .subtitle{{text-align:center;color:#94A3B8;font-size:13px;margin-bottom:24px;}}
    .tabs{{display:flex;gap:4px;margin-bottom:20px;border-bottom:2px solid {GRID_COLOR};}}
    .tab-btn{{padding:10px 24px;background:{GRID_COLOR};color:#94A3B8;border:none;
      cursor:pointer;font-family:{FONT_FAMILY};font-size:14px;
      border-radius:6px 6px 0 0;transition:all 0.2s;}}
    .tab-btn:hover{{background:#2a3050;color:{TEXT_COLOR};}}
    .tab-btn.active{{background:{BG_COLOR};color:{ACCENT};border:2px solid {ACCENT};
      border-bottom:2px solid {BG_COLOR};margin-bottom:-2px;}}
    .tab-content{{display:none;}}
    .tab-content.active{{display:block;}}
  </style>
</head>
<body>
  <h1>Dashboard CCNP ENCORE 350-401 (Modular)</h1>
  <p class="subtitle">Progresso de estudos - estrutura de pastas + analise de commits</p>
  <div class="tabs">
    <button class="tab-btn active" onclick="showTab('resumo')">Resumo Geral</button>
    <button class="tab-btn" onclick="showTab('progresso')">Progresso CCNP</button>
    <button class="tab-btn" onclick="showTab('commits')">Analise de Commits</button>
  </div>
  <div id="resumo" class="tab-content active">{aba1}</div>
  <div id="progresso" class="tab-content">{aba2}</div>
  <div id="commits" class="tab-content">{aba3}</div>
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


def main():
    args = parse_args()
    print(f"\n{'='*55}")
    print(f"  Dashboard Modular — CCNP ENCORE 350-401")
    print(f"  Repositorio : {args.repo}")
    print(f"  Blueprint   : {args.ccnp}")
    print(f"{'='*55}\n")

    validate_repo(args.repo)
    validate_ccnp(args.ccnp)

    lines   = extract_git_log(args.repo)   # modulo extract.py
    records = parse_lines(lines)            # modulo parser.py
    save_csv(records)                       # modulo parser.py
    df      = pd.read_csv(OUTPUT_CSV, parse_dates=["date"])

    domains = scan_blueprint(args.ccnp)    # modulo scanner.py

    print("Gerando dashboard...")
    aba1 = build_aba_resumo(domains, df)
    aba2 = build_aba_progresso(domains)
    aba3 = build_aba_commits(df)

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(build_html(aba1, aba2, aba3))

    print(f"\n Concluido! Abra: {OUTPUT_HTML}\n")


if __name__ == "__main__":
    main()
