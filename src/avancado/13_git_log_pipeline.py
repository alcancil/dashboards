import subprocess
import csv
import os
import argparse
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


DELIMITER = "|"

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_RAW  = os.path.join(BASE_DIR, "data", "raw", "raw_git_log.txt")
OUTPUT_CSV  = os.path.join(BASE_DIR, "data", "processed", "git_log.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "docs", "13_dashboard_git_log.html")

# Dicionário de normalização de verbos
# Chave: variação encontrada nos commits (lowercase)
# Valor: forma canônica padronizada
ACTION_MAP = {
    "alterado":    "Alterado",
    "alteradoo":   "Alterado",
    "aletardo":    "Alterado",
    "aletrado":    "Alterado",
    "alterad":     "Alterado",
    "alterados":   "Alterado",
    "adicionado":  "Adicionado",
    "adicionando": "Adicionado",
    "adicionada":  "Adicionado",
    "adicioando":  "Adicionado",
    "adicioanado": "Adicionado",
    "adiconado":   "Adicionado",
    "ajustado":    "Ajustado",
    "ajuste":      "Ajustado",
    "acertado":    "Acertado",
    "arrumando":   "Acertado",
    "removido":    "Removido",
    "apagado":     "Removido",
    "realizado":   "Realizado",
    "separado":    "Separado",
    "dividido":    "Dividido",
    "criado":      "Criado",
    "corrigido":   "Corrigido",
    "atualizado":  "Atualizado",
    "reanomeado":  "Renomeado",
    "teste":       "Teste",
    "update":      "Atualizado",
    "vault":       "Outro",
    "initial":     "Outro",
}

# Palavras-chave para identificar o domínio CCNP na mensagem
# Cada entrada: (palavra-chave lowercase, nome canônico do domínio)
DOMAIN_KEYWORDS = [
    ("architecture",      "Architecture"),
    ("virtualization",    "Virtualization"),
    ("virtualização",     "Virtualization"),
    ("vrf",               "Infrastructure"),
    ("qos",               "Infrastructure"),
    ("ospf",              "Infrastructure"),
    ("eigrp",             "Infrastructure"),
    ("bgp",               "Infrastructure"),
    ("mpls",              "Infrastructure"),
    ("lisp",              "Infrastructure"),
    ("vxlan",             "Infrastructure"),
    ("stp",               "Infrastructure"),
    ("vlan",              "Infrastructure"),
    ("infrastructure",    "Infrastructure"),
    ("network assurance", "Network Assurance"),
    ("assurance",         "Network Assurance"),
    ("netflow",           "Network Assurance"),
    ("snmp",              "Network Assurance"),
    ("syslog",            "Network Assurance"),
    ("security",          "Security"),
    ("segurança",         "Security"),
    ("acl",               "Security"),
    ("firewall",          "Security"),
    ("vpn",               "Security"),
    ("automation",        "Automation"),
    ("automação",         "Automation"),
    ("python",            "Automation"),
    ("netmiko",           "Automation"),
    ("paramiko",          "Automation"),
    ("ansible",           "Automation"),
    ("parsing",           "Automation"),
    ("multicast",         "Infrastructure"),
    ("pim",               "Infrastructure"),
    ("igmp",              "Infrastructure"),
]

WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_PT    = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

ACTION_COLORS = {
    "Alterado":   "#4B9EFF",
    "Adicionado": "#00C896",
    "Ajustado":   "#FB923C",
    "Acertado":   "#A78BFA",
    "Removido":   "#FF4B4B",
    "Realizado":  "#FACC15",
    "Separado":   "#94A3B8",
    "Dividido":   "#94A3B8",
    "Criado":     "#34D399",
    "Corrigido":  "#F472B6",
    "Atualizado": "#60A5FA",
    "Renomeado":  "#CBD5E1",
    "Teste":      "#FCD34D",
    "Outro":      "#475569",
}

BG_COLOR    = "#0F1117"
GRID_COLOR  = "#1E2130"
TEXT_COLOR  = "#E2E8F0"
FONT_FAMILY = "Courier New, monospace"


# =============================================================================
# ARGUMENTOS
# =============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Pipeline completo: git log → CSV → dashboard HTML.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--repo",
        required=True,
        metavar="REPO",
        help=(
            "Caminho absoluto para o repositório ccnp-enterprise-lab\n"
            "Exemplo Windows : D:\\ESTUDOS\\ccnp-enterprise-lab\n"
            "Exemplo Linux   : /home/user/ccnp-enterprise-lab"
        )
    )
    return parser.parse_args()


def validate_repo(repo_path):
    if not os.path.isdir(repo_path):
        raise FileNotFoundError(f"Repositório não encontrado: {repo_path}")
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        raise ValueError(f"O caminho existe mas não é um repositório Git: {repo_path}")


# =============================================================================
# ETAPA 1 — EXTRAÇÃO
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
    print(f"[1/4] Git log extraído: {len(lines)} commits → {OUTPUT_RAW}")
    return lines


# =============================================================================
# ETAPA 2 — PARSING
# =============================================================================

def extract_action(message):
    first_word = message.strip().split()[0].lower() if message.strip() else ""
    return ACTION_MAP.get(first_word, "Outro")


def extract_domain(message):
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
            "domain":  extract_domain(message),
            "lab":     extract_lab(message),
        })
    print(f"[2/4] Parsing concluído: {len(records)} registros válidos")
    return records


# =============================================================================
# ETAPA 3 — EXPORTAÇÃO CSV
# =============================================================================

def save_csv(records):
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    fieldnames = ["hash", "date", "week", "weekday", "message", "action", "domain", "lab"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"[3/4] CSV salvo: {OUTPUT_CSV}")


# =============================================================================
# ETAPA 4 — DASHBOARD
# =============================================================================

def build_dashboard():
    df = pd.read_csv(OUTPUT_CSV, parse_dates=["date"])

    total_commits = len(df)
    first_commit  = df["date"].min().strftime("%d/%m/%Y")
    last_commit   = df["date"].max().strftime("%d/%m/%Y")
    total_labs    = (df["lab"] == "Sim").sum()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Commits ao longo do tempo",
            "Distribuição por ação",
            "Distribuição por domínio CCNP",
            "Commits por dia da semana vs semana",
        ),
        vertical_spacing=0.18,
        horizontal_spacing=0.12,
        specs=[
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "xy"}, {"type": "xy"}],
        ]
    )

    # --- Gráfico 1: Linha — commits por semana ---
    commits_by_week = df.groupby("week").size().reset_index(name="count")
    commits_by_week = commits_by_week.sort_values("week")
    fig.add_trace(
        go.Scatter(
            x=commits_by_week["week"],
            y=commits_by_week["count"],
            mode="lines+markers",
            line=dict(color="#00C896", width=2),
            marker=dict(size=6, color="#00C896"),
            fill="tozeroy",
            fillcolor="rgba(0,200,150,0.1)",
            name="commits/semana",
            hovertemplate="Semana: %{x}<br>Commits: %{y}<extra></extra>",
        ),
        row=1, col=1
    )

    # --- Gráfico 2: Barras — distribuição por ação ---
    action_counts = df["action"].value_counts()
    colors_action = [ACTION_COLORS.get(a, "#475569") for a in action_counts.index]
    fig.add_trace(
        go.Bar(
            x=action_counts.index.tolist(),
            y=action_counts.values.tolist(),
            marker_color=colors_action,
            name="por ação",
            hovertemplate="Ação: %{x}<br>Commits: %{y}<extra></extra>",
        ),
        row=1, col=2
    )

    # --- Gráfico 3: Barras horizontais — distribuição por domínio ---
    domain_counts = df["domain"].value_counts()
    fig.add_trace(
        go.Bar(
            x=domain_counts.values.tolist(),
            y=domain_counts.index.tolist(),
            orientation="h",
            marker_color="#4B9EFF",
            name="por domínio",
            hovertemplate="Domínio: %{y}<br>Commits: %{x}<extra></extra>",
        ),
        row=2, col=1
    )

    # --- Gráfico 4: Heatmap — dia da semana vs semana ---
    heatmap_pivot = df.groupby(["week", "weekday"]).size().unstack(fill_value=0)
    heatmap_pivot = heatmap_pivot.reindex(columns=WEEKDAY_ORDER, fill_value=0)
    heatmap_pivot = heatmap_pivot.loc[sorted(heatmap_pivot.index)]
    fig.add_trace(
        go.Heatmap(
            z=heatmap_pivot.values.T.tolist(),
            x=heatmap_pivot.index.tolist(),
            y=WEEKDAY_PT,
            colorscale=[
                [0.0,  "#0F1117"],
                [0.01, "#1a2744"],
                [0.3,  "#1d4ed8"],
                [0.6,  "#0ea5e9"],
                [1.0,  "#00C896"],
            ],
            showscale=True,
            colorbar=dict(
                title=dict(text="commits", font=dict(color=TEXT_COLOR)),
                tickfont=dict(color=TEXT_COLOR),
                x=1.02,
            ),
            hovertemplate="Semana: %{x}<br>Dia: %{y}<br>Commits: %{z}<extra></extra>",
            name="heatmap",
        ),
        row=2, col=2
    )

    # --- Cards de totais ---
    cards = [
        (f"{total_commits}", "Total de Commits", 0.12),
        (first_commit,       "Primeiro Commit",  0.37),
        (last_commit,        "Último Commit",    0.62),
        (f"{total_labs}",    "Labs Realizados",  0.87),
    ]
    annotations = []
    for valor, label, x_pos in cards:
        annotations.append(dict(
            text=(
                f"<b style='font-size:22px;color:#00C896'>{valor}</b><br>"
                f"<span style='font-size:11px;color:#94A3B8'>{label}</span>"
            ),
            x=x_pos, y=1.08,
            xref="paper", yref="paper",
            showarrow=False,
            align="center",
            font=dict(family=FONT_FAMILY),
            bgcolor="#1E2130",
            bordercolor="#00C896",
            borderwidth=1,
            borderpad=8,
        ))
    for ann in fig.layout.annotations:
        annotations.append(ann)

    fig.update_layout(
        title=dict(
            text="📊 Git Log Dashboard — CCNP Enterprise Lab",
            font=dict(size=20, color=TEXT_COLOR, family=FONT_FAMILY),
            x=0.5,
        ),
        annotations=annotations,
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=800,
        showlegend=False,
        margin=dict(t=140, b=60, l=60, r=60),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    fig.write_html(OUTPUT_HTML)
    print(f"[4/4] Dashboard salvo: {OUTPUT_HTML}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    args = parse_args()
    print(f"\n{'='*55}")
    print(f"  Pipeline completo: git log → CSV → Dashboard")
    print(f"  Repositório: {args.repo}")
    print(f"{'='*55}\n")
    validate_repo(args.repo)
    lines   = extract_git_log(args.repo)
    records = parse_lines(lines)
    save_csv(records)
    build_dashboard()
    print(f"\n✓ Concluído! Abra: {OUTPUT_HTML}\n")


if __name__ == "__main__":
    main()