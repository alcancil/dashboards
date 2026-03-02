import subprocess
import csv
import os
import argparse
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_RAW  = os.path.join(BASE_DIR, "data", "raw", "raw_git_log.txt")
OUTPUT_CSV  = os.path.join(BASE_DIR, "data", "processed", "git_log.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "docs", "15_dashboard_completo.html")

DELIMITER = "|"

DOMAIN_ORDER = [
    "01 - Architecture",
    "02 - Virtualization",
    "03 - Infrastructure",
    "04 - Network Assurance",
    "05 - Security",
    "06 - Automation",
]

ACTION_MAP = {
    "alterado":    "Alterado",   "alteradoo":   "Alterado",
    "aletardo":    "Alterado",   "aletrado":    "Alterado",
    "alterad":     "Alterado",   "alterados":   "Alterado",
    "adicionado":  "Adicionado", "adicionando": "Adicionado",
    "adicionada":  "Adicionado", "adicioando":  "Adicionado",
    "adicioanado": "Adicionado", "adiconado":   "Adicionado",
    "ajustado":    "Ajustado",   "ajuste":      "Ajustado",
    "acertado":    "Acertado",   "arrumando":   "Acertado",
    "removido":    "Removido",   "apagado":     "Removido",
    "realizado":   "Realizado",  "separado":    "Separado",
    "dividido":    "Dividido",   "criado":      "Criado",
    "corrigido":   "Corrigido",  "atualizado":  "Atualizado",
    "update":      "Atualizado", "reanomeado":  "Renomeado",
    "teste":       "Teste",      "vault":       "Outro",
    "initial":     "Outro",
}

DOMAIN_KEYWORDS = [
    ("architecture", "Architecture"), ("virtualization", "Virtualization"),
    ("virtualização", "Virtualization"), ("vrf", "Infrastructure"),
    ("qos", "Infrastructure"), ("ospf", "Infrastructure"),
    ("eigrp", "Infrastructure"), ("bgp", "Infrastructure"),
    ("mpls", "Infrastructure"), ("lisp", "Infrastructure"),
    ("vxlan", "Infrastructure"), ("stp", "Infrastructure"),
    ("vlan", "Infrastructure"), ("multicast", "Infrastructure"),
    ("pim", "Infrastructure"), ("igmp", "Infrastructure"),
    ("infrastructure", "Infrastructure"), ("network assurance", "Network Assurance"),
    ("assurance", "Network Assurance"), ("netflow", "Network Assurance"),
    ("snmp", "Network Assurance"), ("syslog", "Network Assurance"),
    ("security", "Security"), ("segurança", "Security"),
    ("acl", "Security"), ("firewall", "Security"), ("vpn", "Security"),
    ("automation", "Automation"), ("automação", "Automation"),
    ("python", "Automation"), ("netmiko", "Automation"),
    ("paramiko", "Automation"), ("ansible", "Automation"),
    ("parsing", "Automation"),
]

ACTION_COLORS = {
    "Alterado": "#4B9EFF", "Adicionado": "#00C896", "Ajustado": "#FB923C",
    "Acertado": "#A78BFA", "Removido": "#FF4B4B", "Realizado": "#FACC15",
    "Separado": "#94A3B8", "Dividido": "#94A3B8", "Criado": "#34D399",
    "Corrigido": "#F472B6", "Atualizado": "#60A5FA", "Renomeado": "#CBD5E1",
    "Teste": "#FCD34D", "Outro": "#475569",
}

DOMAIN_COLORS = {
    "01 - Architecture":      "#00C896",
    "02 - Virtualization":    "#4B9EFF",
    "03 - Infrastructure":    "#FB923C",
    "04 - Network Assurance": "#A78BFA",
    "05 - Security":          "#FF4B4B",
    "06 - Automation":        "#FACC15",
}

WEEKDAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
WEEKDAY_PT    = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]

BG_COLOR    = "#0F1117"
GRID_COLOR  = "#1E2130"
TEXT_COLOR  = "#E2E8F0"
ACCENT      = "#00C896"
FONT_FAMILY = "Courier New, monospace"


# =============================================================================
# ARGUMENTOS
# =============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Dashboard completo CCNP — 3 abas: Resumo, Progresso e Git Log.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--repo",
        required=True,
        metavar="REPO",
        help="Caminho para a raiz do repositório Git\nEx: D:\\ESTUDOS\\CISCO\\CISCO"
    )
    parser.add_argument(
        "--ccnp",
        required=True,
        metavar="CCNP",
        help="Caminho para a pasta do Blueprint CCNP ENCOR\nEx: D:\\ESTUDOS\\CISCO\\CISCO\\CCNP 350-401 ENCOR"
    )
    return parser.parse_args()


def validate_paths(repo_path, ccnp_path):
    if not os.path.isdir(repo_path):
        raise FileNotFoundError(f"Repositório não encontrado: {repo_path}")
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        raise ValueError(f"Não é um repositório Git: {repo_path}")
    if not os.path.isdir(ccnp_path):
        raise FileNotFoundError(f"Pasta CCNP não encontrada: {ccnp_path}")


# =============================================================================
# ETAPA 1 — EXTRAÇÃO DO GIT LOG
# =============================================================================

def extract_git_log(repo_path):
    os.makedirs(os.path.dirname(OUTPUT_RAW), exist_ok=True)
    result = subprocess.run(
        ["git", "log", f"--pretty=format:%H{DELIMITER}%ad{DELIMITER}%s", "--date=iso"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"Erro ao executar git log: {result.stderr}")
    with open(OUTPUT_RAW, "w", encoding="utf-8") as f:
        f.write(result.stdout)
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    print(f"[1/4] Git log extraído: {len(lines)} commits")
    return lines


# =============================================================================
# ETAPA 2 — PARSING DO GIT LOG
# =============================================================================

def extract_action(message):
    first_word = message.strip().split()[0].lower() if message.strip() else ""
    return ACTION_MAP.get(first_word, "Outro")


def extract_domain_from_commit(message):
    msg_lower = message.lower()
    for keyword, domain in DOMAIN_KEYWORDS:
        if keyword in msg_lower:
            return domain
    return "Geral"


def extract_lab(message):
    msg_lower = message.lower()
    return "Sim" if "exemplo prático" in msg_lower or "exemplo pratico" in msg_lower else "Não"


def parse_lines(lines):
    records = []
    for line in lines:
        parts = line.split(DELIMITER, maxsplit=2)
        if len(parts) != 3:
            continue
        commit_hash, date_str, message = parts
        try:
            dt = datetime.fromisoformat(date_str.strip()[:19])
        except ValueError:
            continue
        records.append({
            "hash":    commit_hash.strip(),
            "date":    dt.strftime("%Y-%m-%d"),
            "week":    dt.strftime("%Y-W%W"),
            "weekday": dt.strftime("%A"),
            "message": message.strip(),
            "action":  extract_action(message),
            "domain":  extract_domain_from_commit(message),
            "lab":     extract_lab(message),
        })
    print(f"[2/4] Parsing concluído: {len(records)} registros")
    return records


def save_csv(records):
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    fieldnames = ["hash","date","week","weekday","message","action","domain","lab"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"[3/4] CSV salvo: {OUTPUT_CSV}")


# =============================================================================
# ETAPA 3 — LEITURA DA ESTRUTURA DE PASTAS DO BLUEPRINT
# =============================================================================

def scan_blueprint(ccnp_path):
    domains = {}

    for domain_name in DOMAIN_ORDER:
        domain_path = os.path.join(ccnp_path, domain_name)
        if not os.path.isdir(domain_path):
            domains[domain_name] = {"topics": {}, "total_subtopics": 0, "total_labs": 0}
            continue

        topics = {}
        for topic in sorted(os.listdir(domain_path)):
            topic_path = os.path.join(domain_path, topic)
            if not os.path.isdir(topic_path):
                continue
            subtopics = []
            labs = []
            for sub in sorted(os.listdir(topic_path)):
                sub_path = os.path.join(topic_path, sub)
                if not os.path.isdir(sub_path):
                    continue
                if sub in ("Arquivos", "Imagens", "Simulado"):
                    continue
                subtopics.append(sub)
                if "exemplo pr" in sub.lower() or "exemplo pratico" in sub.lower():
                    labs.append(sub)
            topics[topic] = {"subtopics": subtopics, "labs": labs}

        total_subtopics = sum(len(v["subtopics"]) for v in topics.values())
        total_labs      = sum(len(v["labs"]) for v in topics.values())
        domains[domain_name] = {
            "topics":          topics,
            "total_subtopics": total_subtopics,
            "total_labs":      total_labs,
        }

    print(f"[4/4] Blueprint escaneado: {len(domains)} domínios")
    return domains


# =============================================================================
# DASHBOARD — ABA 1: RESUMO GERAL
# =============================================================================

def build_aba_resumo(domains, df):
    total_subtopics  = sum(d["total_subtopics"] for d in domains.values())
    total_labs       = sum(d["total_labs"] for d in domains.values())
    dominios_iniciados = sum(1 for d in domains.values() if d["total_subtopics"] > 0)
    total_commits    = len(df)

    # --- Gráfico 1: Subtópicos por domínio (barras horizontais) ---
    dom_names  = [d.replace("01 - ","").replace("02 - ","").replace("03 - ","")
                   .replace("04 - ","").replace("05 - ","").replace("06 - ","")
                  for d in DOMAIN_ORDER]
    dom_subs   = [domains[d]["total_subtopics"] for d in DOMAIN_ORDER]
    dom_labs   = [domains[d]["total_labs"] for d in DOMAIN_ORDER]
    dom_colors = [DOMAIN_COLORS[d] for d in DOMAIN_ORDER]

    fig1 = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Subtópicos estudados por domínio", "Commits ao longo do tempo"),
        horizontal_spacing=0.12,
    )

    fig1.add_trace(
        go.Bar(
            x=dom_subs,
            y=dom_names,
            orientation="h",
            marker_color=dom_colors,
            name="Subtópicos",
            hovertemplate="Domínio: %{y}<br>Subtópicos: %{x}<extra></extra>",
        ),
        row=1, col=1
    )

    commits_by_week = df.groupby("week").size().reset_index(name="count").sort_values("week")
    fig1.add_trace(
        go.Scatter(
            x=commits_by_week["week"],
            y=commits_by_week["count"],
            mode="lines+markers",
            line=dict(color=ACCENT, width=2),
            marker=dict(size=5, color=ACCENT),
            fill="tozeroy",
            fillcolor="rgba(0,200,150,0.1)",
            name="Commits/semana",
            hovertemplate="Semana: %{x}<br>Commits: %{y}<extra></extra>",
        ),
        row=1, col=2
    )

    fig1.update_layout(
        paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=380, showlegend=False,
        margin=dict(t=50, b=40, l=10, r=10),
    )
    fig1.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig1.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    cards_html = f"""
    <div style="display:flex; gap:16px; margin-bottom:20px; flex-wrap:wrap;">
      <div style="flex:1; min-width:140px; background:#1E2130; border:1px solid {ACCENT};
                  border-radius:8px; padding:16px; text-align:center;">
        <div style="font-size:28px; font-weight:bold; color:{ACCENT};">{total_commits}</div>
        <div style="font-size:12px; color:#94A3B8;">Total de Commits</div>
      </div>
      <div style="flex:1; min-width:140px; background:#1E2130; border:1px solid {ACCENT};
                  border-radius:8px; padding:16px; text-align:center;">
        <div style="font-size:28px; font-weight:bold; color:{ACCENT};">{total_subtopics}</div>
        <div style="font-size:12px; color:#94A3B8;">Subtópicos Criados</div>
      </div>
      <div style="flex:1; min-width:140px; background:#1E2130; border:1px solid {ACCENT};
                  border-radius:8px; padding:16px; text-align:center;">
        <div style="font-size:28px; font-weight:bold; color:{ACCENT};">{total_labs}</div>
        <div style="font-size:12px; color:#94A3B8;">Labs Realizados</div>
      </div>
      <div style="flex:1; min-width:140px; background:#1E2130; border:1px solid {ACCENT};
                  border-radius:8px; padding:16px; text-align:center;">
        <div style="font-size:28px; font-weight:bold; color:{ACCENT};">{dominios_iniciados}/6</div>
        <div style="font-size:12px; color:#94A3B8;">Domínios Iniciados</div>
      </div>
    </div>
    """

    graph_html = pio.to_html(fig1, full_html=False, include_plotlyjs=False)
    return cards_html + graph_html


# =============================================================================
# DASHBOARD — ABA 2: PROGRESSO POR DOMÍNIO
# =============================================================================

def build_aba_progresso(domains):
    dom_names  = [d.split(" - ", 1)[1] for d in DOMAIN_ORDER]
    dom_subs   = [domains[d]["total_subtopics"] for d in DOMAIN_ORDER]
    dom_labs   = [domains[d]["total_labs"] for d in DOMAIN_ORDER]
    dom_colors = [DOMAIN_COLORS[d] for d in DOMAIN_ORDER]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Subtópicos vs Labs por domínio", "Distribuição de subtópicos"),
        specs=[[{"type": "xy"}, {"type": "domain"}]],
        horizontal_spacing=0.12,
    )

    # Barras agrupadas: subtópicos e labs
    fig.add_trace(
        go.Bar(
            name="Subtópicos",
            x=dom_names,
            y=dom_subs,
            marker_color=dom_colors,
            hovertemplate="Domínio: %{x}<br>Subtópicos: %{y}<extra></extra>",
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            name="Labs",
            x=dom_names,
            y=dom_labs,
            marker_color=["rgba(255,75,75,0.8)"] * 6,
            hovertemplate="Domínio: %{x}<br>Labs: %{y}<extra></extra>",
        ),
        row=1, col=1
    )

    # Pizza de distribuição
    dom_subs_nonzero = [s if s > 0 else 0 for s in dom_subs]
    fig.add_trace(
        go.Pie(
            labels=dom_names,
            values=dom_subs_nonzero,
            marker_colors=dom_colors,
            hole=0.4,
            hovertemplate="Domínio: %{label}<br>Subtópicos: %{value}<br>(%{percent})<extra></extra>",
        ),
        row=1, col=2
    )

    fig.update_layout(
        paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=420, barmode="group",
        legend=dict(bgcolor=BG_COLOR, bordercolor=GRID_COLOR, borderwidth=1),
        margin=dict(t=50, b=40, l=10, r=10),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    # Tabela de detalhes por domínio
    table_rows = ""
    for domain in DOMAIN_ORDER:
        d     = domains[domain]
        name  = domain.split(" - ", 1)[1]
        subs  = d["total_subtopics"]
        labs  = d["total_labs"]
        tops  = len(d["topics"])
        color = DOMAIN_COLORS[domain]
        status = "✅ Iniciado" if subs > 0 else "⏳ Pendente"
        table_rows += f"""
        <tr>
          <td style="padding:8px 12px;">
            <span style="display:inline-block; width:12px; height:12px;
                         background:{color}; border-radius:50%; margin-right:8px;"></span>
            {name}
          </td>
          <td style="padding:8px 12px; text-align:center;">{tops}</td>
          <td style="padding:8px 12px; text-align:center;">{subs}</td>
          <td style="padding:8px 12px; text-align:center; color:#FF4B4B;">{labs}</td>
          <td style="padding:8px 12px; text-align:center;">{status}</td>
        </tr>
        """

    table_html = f"""
    <table style="width:100%; border-collapse:collapse; margin-top:20px;
                  background:#1E2130; border-radius:8px; overflow:hidden;
                  font-family: Courier New, monospace; color:{TEXT_COLOR};">
      <thead>
        <tr style="background:#0F1117; border-bottom:1px solid {ACCENT};">
          <th style="padding:10px 12px; text-align:left;">Domínio</th>
          <th style="padding:10px 12px; text-align:center;">Tópicos</th>
          <th style="padding:10px 12px; text-align:center;">Subtópicos</th>
          <th style="padding:10px 12px; text-align:center;">Labs</th>
          <th style="padding:10px 12px; text-align:center;">Status</th>
        </tr>
      </thead>
      <tbody>{table_rows}</tbody>
    </table>
    """

    graph_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
    return graph_html + table_html


# =============================================================================
# DASHBOARD — ABA 3: ANÁLISE DE COMMITS
# =============================================================================

def build_aba_commits(df):
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Commits ao longo do tempo",
            "Distribuição por ação",
            "Distribuição por domínio",
            "Heatmap — dia da semana vs semana",
        ),
        vertical_spacing=0.18,
        horizontal_spacing=0.12,
        specs=[
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "xy"}, {"type": "xy"}],
        ]
    )

    commits_by_week = df.groupby("week").size().reset_index(name="count").sort_values("week")
    fig.add_trace(
        go.Scatter(
            x=commits_by_week["week"], y=commits_by_week["count"],
            mode="lines+markers",
            line=dict(color=ACCENT, width=2),
            marker=dict(size=5, color=ACCENT),
            fill="tozeroy", fillcolor="rgba(0,200,150,0.1)",
            hovertemplate="Semana: %{x}<br>Commits: %{y}<extra></extra>",
        ), row=1, col=1
    )

    action_counts = df["action"].value_counts()
    fig.add_trace(
        go.Bar(
            x=action_counts.index.tolist(),
            y=action_counts.values.tolist(),
            marker_color=[ACTION_COLORS.get(a, "#475569") for a in action_counts.index],
            hovertemplate="Ação: %{x}<br>Commits: %{y}<extra></extra>",
        ), row=1, col=2
    )

    domain_counts = df["domain"].value_counts()
    fig.add_trace(
        go.Bar(
            x=domain_counts.values.tolist(),
            y=domain_counts.index.tolist(),
            orientation="h",
            marker_color="#4B9EFF",
            hovertemplate="Domínio: %{y}<br>Commits: %{x}<extra></extra>",
        ), row=2, col=1
    )

    heatmap_pivot = df.groupby(["week","weekday"]).size().unstack(fill_value=0)
    heatmap_pivot = heatmap_pivot.reindex(columns=WEEKDAY_ORDER, fill_value=0)
    heatmap_pivot = heatmap_pivot.loc[sorted(heatmap_pivot.index)]
    fig.add_trace(
        go.Heatmap(
            z=heatmap_pivot.values.T.tolist(),
            x=heatmap_pivot.index.tolist(),
            y=WEEKDAY_PT,
            colorscale=[
                [0.0, "#0F1117"], [0.01, "#1a2744"],
                [0.3, "#1d4ed8"], [0.6, "#0ea5e9"], [1.0, ACCENT],
            ],
            showscale=True,
            colorbar=dict(
                title=dict(text="commits", font=dict(color=TEXT_COLOR)),
                tickfont=dict(color=TEXT_COLOR), x=1.02,
            ),
            hovertemplate="Semana: %{x}<br>Dia: %{y}<br>Commits: %{z}<extra></extra>",
        ), row=2, col=2
    )

    fig.update_layout(
        paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=700, showlegend=False,
        margin=dict(t=50, b=40, l=10, r=60),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    total_commits = len(df)
    total_labs    = (df["lab"] == "Sim").sum()
    first_commit  = df["date"].min().strftime("%d/%m/%Y")
    last_commit   = df["date"].max().strftime("%d/%m/%Y")

    cards_html = f"""
    <div style="display:flex; gap:16px; margin-bottom:20px; flex-wrap:wrap;">
      <div style="flex:1; min-width:140px; background:#1E2130; border:1px solid {ACCENT};
                  border-radius:8px; padding:16px; text-align:center;">
        <div style="font-size:28px; font-weight:bold; color:{ACCENT};">{total_commits}</div>
        <div style="font-size:12px; color:#94A3B8;">Total de Commits</div>
      </div>
      <div style="flex:1; min-width:140px; background:#1E2130; border:1px solid {ACCENT};
                  border-radius:8px; padding:16px; text-align:center;">
        <div style="font-size:28px; font-weight:bold; color:{ACCENT};">{first_commit}</div>
        <div style="font-size:12px; color:#94A3B8;">Primeiro Commit</div>
      </div>
      <div style="flex:1; min-width:140px; background:#1E2130; border:1px solid {ACCENT};
                  border-radius:8px; padding:16px; text-align:center;">
        <div style="font-size:28px; font-weight:bold; color:{ACCENT};">{last_commit}</div>
        <div style="font-size:12px; color:#94A3B8;">Último Commit</div>
      </div>
      <div style="flex:1; min-width:140px; background:#1E2130; border:1px solid {ACCENT};
                  border-radius:8px; padding:16px; text-align:center;">
        <div style="font-size:28px; font-weight:bold; color:{ACCENT};">{total_labs}</div>
        <div style="font-size:12px; color:#94A3B8;">Labs nos Commits</div>
      </div>
    </div>
    """

    return cards_html + pio.to_html(fig, full_html=False, include_plotlyjs=False)


# =============================================================================
# MONTA O HTML FINAL COM AS 3 ABAS
# =============================================================================

def build_html(aba1_html, aba2_html, aba3_html):
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard CCNP ENCORE 350-401</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: {BG_COLOR};
      color: {TEXT_COLOR};
      font-family: {FONT_FAMILY};
      padding: 24px;
    }}
    h1 {{
      text-align: center;
      color: {ACCENT};
      font-size: 22px;
      margin-bottom: 8px;
    }}
    .subtitle {{
      text-align: center;
      color: #94A3B8;
      font-size: 13px;
      margin-bottom: 24px;
    }}
    .tabs {{
      display: flex;
      gap: 4px;
      margin-bottom: 20px;
      border-bottom: 2px solid {GRID_COLOR};
    }}
    .tab-btn {{
      padding: 10px 24px;
      background: {GRID_COLOR};
      color: #94A3B8;
      border: none;
      cursor: pointer;
      font-family: {FONT_FAMILY};
      font-size: 14px;
      border-radius: 6px 6px 0 0;
      transition: all 0.2s;
    }}
    .tab-btn:hover {{ background: #2a3050; color: {TEXT_COLOR}; }}
    .tab-btn.active {{
      background: {BG_COLOR};
      color: {ACCENT};
      border: 2px solid {ACCENT};
      border-bottom: 2px solid {BG_COLOR};
      margin-bottom: -2px;
    }}
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; }}
  </style>
</head>
<body>
  <h1>📊 Dashboard CCNP ENCORE 350-401</h1>
  <p class="subtitle">Progresso de estudos — estrutura de pastas + análise de commits</p>

  <div class="tabs">
    <button class="tab-btn active" onclick="showTab('resumo')">🏠 Resumo Geral</button>
    <button class="tab-btn" onclick="showTab('progresso')">📈 Progresso CCNP</button>
    <button class="tab-btn" onclick="showTab('commits')">🔍 Análise de Commits</button>
  </div>

  <div id="resumo" class="tab-content active">{aba1_html}</div>
  <div id="progresso" class="tab-content">{aba2_html}</div>
  <div id="commits" class="tab-content">{aba3_html}</div>

  <script>
    function showTab(name) {{
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
      document.getElementById(name).classList.add('active');
      event.target.classList.add('active');
    }}
  </script>
</body>
</html>"""
    return html


# =============================================================================
# MAIN
# =============================================================================

def main():
    args = parse_args()
    print(f"\n{'='*55}")
    print(f"  Dashboard Completo — CCNP ENCORE 350-401")
    print(f"  Repositório : {args.repo}")
    print(f"  Blueprint   : {args.ccnp}")
    print(f"{'='*55}\n")

    validate_paths(args.repo, args.ccnp)

    lines   = extract_git_log(args.repo)
    records = parse_lines(lines)
    save_csv(records)
    df      = pd.read_csv(OUTPUT_CSV, parse_dates=["date"])

    domains = scan_blueprint(args.ccnp)

    print("Gerando dashboard...")
    aba1 = build_aba_resumo(domains, df)
    aba2 = build_aba_progresso(domains)
    aba3 = build_aba_commits(df)

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(build_html(aba1, aba2, aba3))

    print(f"\n✓ Concluído! Abra: {OUTPUT_HTML}\n")


if __name__ == "__main__":
    main()