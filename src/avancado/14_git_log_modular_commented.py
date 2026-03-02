# =============================================================================
# 14_git_log_modular_commented.py
# Orquestrador do pipeline modular: git log → CSV → Dashboard
#
# O que mudou em relação ao script 13 (monolítico):
#   Antes: todas as funções dentro de um único script
#   Agora: funções de extração e parsing vivem em módulos reutilizáveis
#
# Arquitetura de módulos:
#   scripts/parsing/git_log/extract.py → validate_repo, extract_git_log
#   scripts/parsing/git_log/parser.py  → parse_lines, save_csv
#   src/avancado/14_git_log_modular.py → parse_args, build_dashboard, main (orquestrador)
#
# Por que modularizar?
#   - Reutilização: outro script pode importar extract_git_log sem copiar código
#   - Testabilidade: cada módulo pode ser testado de forma independente
#   - Manutenção: mudança na lógica de parsing → altera só parser.py
#   - Separação de responsabilidades: cada arquivo tem uma responsabilidade clara
#
# Uso:
#   python src/avancado/14_git_log_modular.py --repo <caminho_do_repositório>
#
# Exemplos:
#   Windows : python src/avancado/14_git_log_modular.py --repo D:\ESTUDOS\ccnp-enterprise-lab
#   Linux   : python src/avancado/14_git_log_modular.py --repo /home/user/ccnp-enterprise-lab
# =============================================================================

import argparse  # Parsing de argumentos de linha de comando com --help automático
import os        # Manipulação de caminhos portáveis entre Windows e Linux
import sys       # Manipulação do caminho de busca de módulos (sys.path)

import pandas as pd                        # Manipulação de dados tabulares
import plotly.graph_objects as go          # Criação de gráficos Plotly
from plotly.subplots import make_subplots  # Layout com múltiplos gráficos

# BASE_DIR: sobe 2 níveis a partir de src/avancado/ para chegar à raiz do projeto
#   src/avancado/ → (1) src/ → (2) DASHBOARDS/ (raiz)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# sys.path.insert(0, BASE_DIR) adiciona a raiz do projeto ao início do caminho de busca
# Isso permite que o Python encontre a pasta scripts/ como pacote
# Sem isso, o import abaixo falharia com ModuleNotFoundError
sys.path.insert(0, BASE_DIR)

# Importa as funções dos módulos do pacote scripts/parsing/git_log/
# Cada import traz apenas o que este script precisa — sem código duplicado
from scripts.parsing.git_log.extract import validate_repo, extract_git_log
from scripts.parsing.git_log.parser  import parse_lines, save_csv


# Caminhos de output do orquestrador
OUTPUT_CSV  = os.path.join(BASE_DIR, "data", "processed", "git_log.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "docs", "14_dashboard_git_log_modular.html")

# Cores por ação — usadas no gráfico de barras
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

# Ordem dos dias para o heatmap
WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_PT    = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

# Tema visual — estilo terminal escuro (igual aos scripts anteriores)
BG_COLOR    = "#0F1117"
GRID_COLOR  = "#1E2130"
TEXT_COLOR  = "#E2E8F0"
FONT_FAMILY = "Courier New, monospace"


# =============================================================================
# ARGUMENTOS DE LINHA DE COMANDO
# Idêntico ao script 13 — o orquestrador ainda precisa receber o --repo
# =============================================================================

def parse_args():
    # RawTextHelpFormatter preserva quebras de linha no texto do --help
    parser = argparse.ArgumentParser(
        description="Pipeline modular: git log → CSV → dashboard HTML.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # --repo é obrigatório — sem ele o argparse exibe erro e encerra
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
    # parse_args() lê sys.argv e retorna namespace com os atributos
    return parser.parse_args()


# =============================================================================
# ETAPA 4 — DASHBOARD (permanece no orquestrador)
# A visualização é responsabilidade do script de apresentação,
# não dos módulos de extração/parsing — por isso fica aqui
# =============================================================================

def build_dashboard():
    # Lê o CSV gerado pela etapa anterior (save_csv do módulo parser.py)
    # parse_dates converte a coluna "date" para datetime automaticamente
    df = pd.read_csv(OUTPUT_CSV, parse_dates=["date"])

    # Métricas para os cards informativos no topo do dashboard
    total_commits = len(df)                               # total de linhas do CSV
    first_commit  = df["date"].min().strftime("%d/%m/%Y") # data mais antiga
    last_commit   = df["date"].max().strftime("%d/%m/%Y") # data mais recente
    total_labs    = (df["lab"] == "Sim").sum()            # boolean mask → contagem

    # make_subplots cria o layout de grade 2x2
    # specs → tipo de cada subplot: "xy" = eixos cartesianos padrão
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

    # -------------------------------------------------------------------------
    # Gráfico 1: Linha — commits por semana
    # groupby("week").size() conta commits por semana
    # reset_index(name="count") transforma em DataFrame com coluna "count"
    # fill="tozeroy" preenche a área abaixo da linha (area chart)
    # -------------------------------------------------------------------------
    commits_by_week = df.groupby("week").size().reset_index(name="count")
    commits_by_week = commits_by_week.sort_values("week")
    fig.add_trace(
        go.Scatter(
            x=commits_by_week["week"],           # eixo X: semanas
            y=commits_by_week["count"],           # eixo Y: quantidade de commits
            mode="lines+markers",                 # linha com pontos marcados
            line=dict(color="#00C896", width=2),  # cor e espessura da linha
            marker=dict(size=6, color="#00C896"), # tamanho e cor dos pontos
            fill="tozeroy",                       # preenche área até o zero
            fillcolor="rgba(0,200,150,0.1)",      # cor da área com transparência
            name="commits/semana",
            hovertemplate="Semana: %{x}<br>Commits: %{y}<extra></extra>",
        ),
        row=1, col=1  # posição na grade: linha 1, coluna 1
    )

    # -------------------------------------------------------------------------
    # Gráfico 2: Barras — distribuição por ação
    # value_counts() ordena do mais frequente para o menos frequente
    # list comprehension aplica cor por ação via ACTION_COLORS
    # -------------------------------------------------------------------------
    action_counts = df["action"].value_counts()
    colors_action = [ACTION_COLORS.get(a, "#475569") for a in action_counts.index]
    fig.add_trace(
        go.Bar(
            x=action_counts.index.tolist(),  # eixo X: nomes das ações
            y=action_counts.values.tolist(), # eixo Y: quantidade de commits
            marker_color=colors_action,      # cor diferente por ação
            name="por ação",
            hovertemplate="Ação: %{x}<br>Commits: %{y}<extra></extra>",
        ),
        row=1, col=2  # posição na grade: linha 1, coluna 2
    )

    # -------------------------------------------------------------------------
    # Gráfico 3: Barras horizontais — distribuição por domínio CCNP
    # orientation="h" inverte os eixos: X=quantidade, Y=nome do domínio
    # -------------------------------------------------------------------------
    domain_counts = df["domain"].value_counts()
    fig.add_trace(
        go.Bar(
            x=domain_counts.values.tolist(), # eixo X: quantidade de commits
            y=domain_counts.index.tolist(),  # eixo Y: nomes dos domínios
            orientation="h",                 # barras na horizontal
            marker_color="#4B9EFF",
            name="por domínio",
            hovertemplate="Domínio: %{y}<br>Commits: %{x}<extra></extra>",
        ),
        row=2, col=1  # posição na grade: linha 2, coluna 1
    )

    # -------------------------------------------------------------------------
    # Gráfico 4: Heatmap — commits por dia da semana vs semana
    # unstack()  → transforma weekday em colunas (pivot table)
    # reindex()  → garante que todos os dias apareçam mesmo sem dados
    # .values.T  → transpõe: dias ficam no eixo Y, semanas no eixo X
    # -------------------------------------------------------------------------
    heatmap_pivot = df.groupby(["week", "weekday"]).size().unstack(fill_value=0)
    heatmap_pivot = heatmap_pivot.reindex(columns=WEEKDAY_ORDER, fill_value=0)
    heatmap_pivot = heatmap_pivot.loc[sorted(heatmap_pivot.index)]
    fig.add_trace(
        go.Heatmap(
            z=heatmap_pivot.values.T.tolist(), # matriz de valores (dias × semanas)
            x=heatmap_pivot.index.tolist(),    # eixo X: semanas
            y=WEEKDAY_PT,                      # eixo Y: dias em português
            colorscale=[
                [0.0,  "#0F1117"],   # 0 commits → cor de fundo
                [0.01, "#1a2744"],   # 1 commit  → azul muito escuro
                [0.3,  "#1d4ed8"],   # poucos    → azul médio
                [0.6,  "#0ea5e9"],   # médio     → azul claro
                [1.0,  "#00C896"],   # máximo    → verde destaque
            ],
            showscale=True,
            colorbar=dict(
                title=dict(text="commits", font=dict(color=TEXT_COLOR)),
                tickfont=dict(color=TEXT_COLOR),
                x=1.02,  # posição da barra de escala
            ),
            hovertemplate="Semana: %{x}<br>Dia: %{y}<br>Commits: %{z}<extra></extra>",
            name="heatmap",
        ),
        row=2, col=2  # posição na grade: linha 2, coluna 2
    )

    # -------------------------------------------------------------------------
    # Cards de totais via annotations
    # xref/yref="paper" → coordenadas relativas ao canvas (0.0 a 1.0)
    # y=1.08 → posiciona acima dos subplots
    # -------------------------------------------------------------------------
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
    # Preserva os títulos dos subplots gerados pelo make_subplots
    for ann in fig.layout.annotations:
        annotations.append(ann)

    # update_layout aplica configurações globais ao dashboard inteiro
    fig.update_layout(
        title=dict(
            text="📊 Git Log Dashboard — CCNP Enterprise Lab (Modular)",
            font=dict(size=20, color=TEXT_COLOR, family=FONT_FAMILY),
            x=0.5,  # centraliza o título
        ),
        annotations=annotations,
        paper_bgcolor=BG_COLOR,  # fundo externo
        plot_bgcolor=BG_COLOR,   # fundo interno dos gráficos
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=800,
        showlegend=False,
        margin=dict(t=140, b=60, l=60, r=60),
    )
    # Aplica grid escuro em todos os eixos de todos os subplots de uma vez
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    # write_html gera o arquivo HTML interativo com Plotly embutido
    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    fig.write_html(OUTPUT_HTML)
    print(f"[4/4] Dashboard salvo: {OUTPUT_HTML}")


# =============================================================================
# MAIN — Orquestrador
# Chama as funções importadas dos módulos na ordem correta do pipeline
# Note como o main ficou mais limpo: ele apenas coordena, não processa
# =============================================================================

def main():
    args = parse_args()  # lê e valida os argumentos da linha de comando
    print(f"\n{'='*55}")
    print(f"  Pipeline modular: git log → CSV → Dashboard")
    print(f"  Repositório: {args.repo}")
    print(f"{'='*55}\n")
    validate_repo(args.repo)              # módulo extract.py
    lines   = extract_git_log(args.repo) # módulo extract.py → [1/4]
    records = parse_lines(lines)          # módulo parser.py  → [2/4]
    save_csv(records)                     # módulo parser.py  → [3/4]
    build_dashboard()                     # orquestrador      → [4/4]
    print(f"\n✓ Concluído! Abra: {OUTPUT_HTML}\n")


# if __name__ == "__main__" garante que main() só executa quando o script
# é chamado diretamente — não quando importado como módulo por outro script
if __name__ == "__main__":
    main()
