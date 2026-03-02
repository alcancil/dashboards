import argparse
import os
import sys

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from scripts.parsing.git_log.extract import validate_repo, extract_git_log
from scripts.parsing.git_log.parser  import parse_lines, save_csv


OUTPUT_CSV  = os.path.join(BASE_DIR, "data", "processed", "git_log.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "docs", "14_dashboard_git_log_modular.html")

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

WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_PT    = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

BG_COLOR    = "#0F1117"
GRID_COLOR  = "#1E2130"
TEXT_COLOR  = "#E2E8F0"
FONT_FAMILY = "Courier New, monospace"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pipeline modular: git log → CSV → dashboard HTML.",
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
            text="📊 Git Log Dashboard — CCNP Enterprise Lab (Modular)",
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


def main():
    args = parse_args()
    print(f"\n{'='*55}")
    print(f"  Pipeline modular: git log → CSV → Dashboard")
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
