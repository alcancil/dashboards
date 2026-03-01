# =============================================================================
# 13_git_log_pipeline_commented.py
# Pipeline completo: git log → CSV → Dashboard
#
# O que este script faz (4 etapas em sequência):
#   [1/4] EXTRAÇÃO   — executa 'git log' no repositório e salva output bruto
#   [2/4] PARSING    — lê o arquivo bruto, separa campos e enriquece os dados
#   [3/4] CSV        — salva os registros estruturados em git_log.csv
#   [4/4] DASHBOARD  — lê o CSV e gera dashboard HTML com 4 gráficos
#
# Filosofia de parsing: sem regex — apenas split(), strip(), lower() e 'in'
# Isso torna o código mais legível, didático e fácil de manutenção.
#
# Uso:
#   python 13_git_log_pipeline.py --repo <caminho_do_repositório>
#
# Exemplos:
#   Windows : python 13_git_log_pipeline.py --repo D:\ESTUDOS\ccnp-enterprise-lab
#   Linux   : python 13_git_log_pipeline.py --repo /home/user/ccnp-enterprise-lab
# =============================================================================

import subprocess   # Executa comandos do sistema operacional (git log)
import csv          # Leitura e escrita de arquivos CSV
import os           # Manipulação de caminhos portáveis entre Windows e Linux
import argparse     # Parsing de argumentos de linha de comando com --help automático
from datetime import datetime  # Conversão e formatação de datas

import pandas as pd                        # Manipulação de dados tabulares
import plotly.graph_objects as go          # Criação de gráficos Plotly
from plotly.subplots import make_subplots  # Layout com múltiplos gráficos


# =============================================================================
# CONSTANTES DE CONFIGURAÇÃO
# =============================================================================

DELIMITER = "|"

# BASE_DIR: sobe 3 níveis a partir deste script para chegar à raiz do projeto
#   src/avancado/ → src/ → DASHBOARDS/
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_RAW  = os.path.join(BASE_DIR, "data", "raw", "raw_git_log.txt")
OUTPUT_CSV  = os.path.join(BASE_DIR, "data", "processed", "git_log.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "docs", "13_dashboard_git_log.html")

# -----------------------------------------------------------------------------
# DICIONÁRIO DE NORMALIZAÇÃO DE VERBOS (ACTION_MAP)
#
# Problema: o repositório CCNP ainda não usa Conventional Commits,
# então as mensagens têm variações e typos nos verbos de ação.
#
# Solução sem regex: dicionário de lookup simples.
# Pegamos a primeira palavra da mensagem, convertemos para lowercase,
# e buscamos no dicionário para obter a forma canônica padronizada.
#
# Exemplos reais encontrados no git log:
#   "alteradoo" → typo → normaliza para "Alterado"
#   "aletardo"  → typo → normaliza para "Alterado"
#   "alterad"   → typo → normaliza para "Alterado"
#   "aletrado"  → typo → normaliza para "Alterado"
# -----------------------------------------------------------------------------
ACTION_MAP = {
    "alterado":    "Alterado",
    "alteradoo":   "Alterado",   # typo frequente
    "aletardo":    "Alterado",   # typo frequente
    "aletrado":    "Alterado",   # typo frequente
    "alterad":     "Alterado",   # typo (faltou o 'o')
    "alterados":   "Alterado",   # plural → singular
    "adicionado":  "Adicionado",
    "adicionando": "Adicionado", # gerúndio → infinitivo
    "adicionada":  "Adicionado", # feminino → masculino
    "adicioando":  "Adicionado", # typo
    "adicioanado": "Adicionado", # typo
    "adiconado":   "Adicionado", # typo
    "ajustado":    "Ajustado",
    "ajuste":      "Ajustado",
    "acertado":    "Acertado",
    "arrumando":   "Acertado",   # sinônimo informal
    "removido":    "Removido",
    "apagado":     "Removido",   # sinônimo
    "realizado":   "Realizado",
    "separado":    "Separado",
    "dividido":    "Dividido",
    "criado":      "Criado",
    "corrigido":   "Corrigido",
    "atualizado":  "Atualizado",
    "update":      "Atualizado", # inglês → português
    "reanomeado":  "Renomeado",  # typo de 'renomeado'
    "teste":       "Teste",
    "vault":       "Outro",      # commit de ferramenta
    "initial":     "Outro",      # commit inicial do git
}

# -----------------------------------------------------------------------------
# PALAVRAS-CHAVE PARA IDENTIFICAÇÃO DE DOMÍNIO CCNP (DOMAIN_KEYWORDS)
#
# O repositório CCNP organiza o conteúdo nos 6 domínios do exame ENCORE 350-401:
#   1. Architecture
#   2. Virtualization
#   3. Infrastructure
#   4. Network Assurance
#   5. Security
#   6. Automation
#
# Estratégia: verificamos se alguma palavra-chave está contida na mensagem
# usando o operador 'in' após converter tudo para lowercase.
# A lista é percorrida em ordem — a primeira correspondência vence.
# Por isso palavras mais específicas vêm antes das mais genéricas.
# -----------------------------------------------------------------------------
DOMAIN_KEYWORDS = [
    # Domínio: Architecture
    ("architecture",      "Architecture"),

    # Domínio: Virtualization
    ("virtualization",    "Virtualization"),
    ("virtualização",     "Virtualization"),

    # Domínio: Infrastructure (protocolos e tecnologias de rede)
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
    ("multicast",         "Infrastructure"),
    ("pim",               "Infrastructure"),
    ("igmp",              "Infrastructure"),
    ("infrastructure",    "Infrastructure"),

    # Domínio: Network Assurance
    ("network assurance", "Network Assurance"),
    ("assurance",         "Network Assurance"),
    ("netflow",           "Network Assurance"),
    ("snmp",              "Network Assurance"),
    ("syslog",            "Network Assurance"),

    # Domínio: Security
    ("security",          "Security"),
    ("segurança",         "Security"),
    ("acl",               "Security"),
    ("firewall",          "Security"),
    ("vpn",               "Security"),

    # Domínio: Automation
    ("automation",        "Automation"),
    ("automação",         "Automation"),
    ("python",            "Automation"),
    ("netmiko",           "Automation"),
    ("paramiko",          "Automation"),
    ("ansible",           "Automation"),
    ("parsing",           "Automation"),
]

# Ordem para o heatmap (eixo Y)
WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_PT    = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

# Cores por ação (usadas no gráfico de barras)
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

# Tema visual — estilo terminal escuro
BG_COLOR    = "#0F1117"
GRID_COLOR  = "#1E2130"
TEXT_COLOR  = "#E2E8F0"
FONT_FAMILY = "Courier New, monospace"


# =============================================================================
# ARGUMENTOS DE LINHA DE COMANDO
# =============================================================================

def parse_args():
    # ArgumentParser cria o parser com descrição do script
    # RawTextHelpFormatter preserva quebras de linha no texto do --help
    parser = argparse.ArgumentParser(
        description="Pipeline completo: git log → CSV → dashboard HTML.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # add_argument define o argumento --repo
    # required=True  → erro automático se não for passado
    # metavar="REPO" → nome exibido no --help
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
    # parse_args() lê sys.argv, valida e retorna objeto com os atributos
    # Acesso posterior: args.repo
    return parser.parse_args()


def validate_repo(repo_path):
    # Fail fast: verifica tudo antes de executar qualquer etapa
    # Evita erros confusos no meio da execução do pipeline

    # os.path.isdir verifica se o caminho existe e é um diretório
    if not os.path.isdir(repo_path):
        raise FileNotFoundError(f"Repositório não encontrado: {repo_path}")

    # Todo repositório Git possui uma pasta oculta .git na raiz
    # Se ela não existir, o caminho informado não é um repositório Git válido
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        raise ValueError(f"O caminho existe mas não é um repositório Git: {repo_path}")


# =============================================================================
# ETAPA 1 — EXTRAÇÃO
# =============================================================================

def extract_git_log(repo_path):
    # exist_ok=True evita erro se o diretório já existir
    os.makedirs(os.path.dirname(OUTPUT_RAW), exist_ok=True)

    # subprocess.run executa o git log dentro do repositório informado
    # Lista de strings evita problemas com espaços nos caminhos
    # cwd=repo_path   → muda o diretório de trabalho para o repositório
    # capture_output  → captura stdout e stderr sem imprimir no terminal
    # text=True       → decodifica bytes para string automaticamente
    # encoding="utf-8"→ necessário para commits com caracteres especiais (ç, ã)
    result = subprocess.run(
        ["git", "log", f"--pretty=format:%H{DELIMITER}%ad{DELIMITER}%s", "--date=iso"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    # returncode != 0 indica que o git encontrou um erro na execução
    if result.returncode != 0:
        raise RuntimeError(f"Erro ao executar git log: {result.stderr}")

    # Salva o output bruto — fonte da verdade, nunca editar manualmente
    # Este arquivo está no .gitignore pois contém paths locais da máquina
    with open(OUTPUT_RAW, "w", encoding="utf-8") as f:
        f.write(result.stdout)

    # splitlines() divide o output em lista de linhas
    # O filtro 'if l.strip()' remove linhas vazias antes de contar
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    print(f"[1/4] Git log extraído: {len(lines)} commits → {OUTPUT_RAW}")
    return lines


# =============================================================================
# ETAPA 2 — PARSING (funções auxiliares)
# Filosofia: sem regex — apenas operações básicas de string
# =============================================================================

def extract_action(message):
    # split() divide a mensagem em palavras pelo espaço
    # [0] pega a primeira palavra (o verbo de ação)
    # .lower() converte para minúsculo para comparação uniforme
    # .get(first_word, "Outro") busca no dicionário; retorna "Outro" se não encontrar
    first_word = message.strip().split()[0].lower() if message.strip() else ""
    return ACTION_MAP.get(first_word, "Outro")


def extract_domain(message):
    # Converte a mensagem inteira para lowercase uma única vez
    # Depois verifica se cada palavra-chave está contida na mensagem
    # O operador 'in' funciona como substring search — sem regex
    # A primeira correspondência encontrada é retornada (ordem importa)
    msg_lower = message.lower()
    for keyword, domain in DOMAIN_KEYWORDS:
        if keyword in msg_lower:
            return domain
    return "Geral"  # nenhuma palavra-chave encontrada


def extract_lab(message):
    # Verifica se a mensagem menciona "Exemplo Prático" ou "Exemplo Pratico"
    # (com e sem acento) — padrão usado para nomear pastas de laboratório
    # Retorna "Sim"/"Não" (string) para facilitar leitura no CSV
    msg_lower = message.lower()
    return "Sim" if "exemplo prático" in msg_lower or "exemplo pratico" in msg_lower else "Não"


# =============================================================================
# ETAPA 2 — PARSING (função principal)
# Gera lista de dicionários com 8 campos:
#   hash, date, week, weekday, message, action, domain, lab
# =============================================================================

def parse_lines(lines):
    records = []  # lista que vai acumular os dicionários de cada commit
    for line in lines:
        # maxsplit=2 garante que "|" no texto da mensagem não quebre o parse
        # Ex: "hash|2026-02-26 10:30:00 -0300|feat: msg com | barra"
        #   → ["hash", "2026-02-26 10:30:00 -0300", "feat: msg com | barra"]
        parts = line.split(DELIMITER, maxsplit=2)
        # Descarta linhas com formato inesperado (menos de 3 campos)
        if len(parts) != 3:
            continue
        # Desempacota os 3 campos em variáveis separadas
        commit_hash, date_str, message = parts
        try:
            # --date=iso gera: "2026-02-26 10:30:00 -0300"
            # [:19] pega só "2026-02-26 10:30:00" — ignora o timezone
            # fromisoformat converte a string para objeto datetime
            dt = datetime.fromisoformat(date_str.strip()[:19])
        except ValueError:
            continue  # descarta registros com data em formato inesperado
        records.append({
            "hash":    commit_hash.strip(),
            "date":    dt.strftime("%Y-%m-%d"),  # Ex: 2026-02-26
            "week":    dt.strftime("%Y-W%W"),     # Ex: 2026-W08 (agrupamento temporal)
            "weekday": dt.strftime("%A"),         # Ex: Thursday (para o heatmap)
            "message": message.strip(),
            "action":  extract_action(message),   # Ex: Adicionado
            "domain":  extract_domain(message),   # Ex: Infrastructure
            "lab":     extract_lab(message),      # Ex: Sim ou Não
        })
    print(f"[2/4] Parsing concluído: {len(records)} registros válidos")
    return records


# =============================================================================
# ETAPA 3 — EXPORTAÇÃO CSV
# =============================================================================

def save_csv(records):
    # exist_ok=True evita erro se o diretório já existir
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    # fieldnames define a ordem das colunas no arquivo CSV
    fieldnames = ["hash", "date", "week", "weekday", "message", "action", "domain", "lab"]
    # newline="" é recomendado no Windows para evitar linhas em branco extras
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()      # escreve a linha de cabeçalho com os nomes das colunas
        writer.writerows(records) # escreve todos os registros de uma vez
    print(f"[3/4] CSV salvo: {OUTPUT_CSV}")


# =============================================================================
# ETAPA 4 — DASHBOARD
# 4 gráficos em grade 2x2:
#   [1,1] Linha    — commits ao longo do tempo (por semana)
#   [1,2] Barras   — distribuição por ação (verbo normalizado)
#   [2,1] Barras H — distribuição por domínio CCNP
#   [2,2] Heatmap  — commits por dia da semana vs semana
# =============================================================================

def build_dashboard():
    # parse_dates converte a coluna "date" para datetime automaticamente
    df = pd.read_csv(OUTPUT_CSV, parse_dates=["date"])

    # Métricas para os cards informativos no topo do dashboard
    total_commits = len(df)                              # total de linhas do CSV
    first_commit  = df["date"].min().strftime("%d/%m/%Y") # data mais antiga
    last_commit   = df["date"].max().strftime("%d/%m/%Y") # data mais recente
    # Conta quantos commits têm lab == "Sim" (boolean mask)
    total_labs    = (df["lab"] == "Sim").sum()

    # make_subplots cria o layout de grade 2x2
    # rows/cols     → dimensões da grade
    # subplot_titles → títulos de cada célula da grade
    # vertical_spacing / horizontal_spacing → espaço entre gráficos (0.0 a 1.0)
    # specs         → tipo de cada subplot: "xy" = eixos cartesianos padrão
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
    # groupby("week").size() conta quantos commits existem em cada semana
    # reset_index(name="count") transforma o resultado em DataFrame com coluna "count"
    # sort_values("week") garante ordem cronológica no eixo X
    # fill="tozeroy" preenche a área abaixo da linha (area chart)
    # -------------------------------------------------------------------------
    commits_by_week = df.groupby("week").size().reset_index(name="count")
    commits_by_week = commits_by_week.sort_values("week")
    fig.add_trace(
        go.Scatter(
            x=commits_by_week["week"],          # eixo X: semanas
            y=commits_by_week["count"],          # eixo Y: quantidade de commits
            mode="lines+markers",                # linha com pontos marcados
            line=dict(color="#00C896", width=2), # cor e espessura da linha
            marker=dict(size=6, color="#00C896"),# tamanho e cor dos pontos
            fill="tozeroy",                      # preenche área até o zero
            fillcolor="rgba(0,200,150,0.1)",     # cor da área com transparência
            name="commits/semana",
            hovertemplate="Semana: %{x}<br>Commits: %{y}<extra></extra>",
        ),
        row=1, col=1  # posição na grade: linha 1, coluna 1
    )

    # -------------------------------------------------------------------------
    # Gráfico 2: Barras — distribuição por ação
    # value_counts() ordena do mais frequente para o menos frequente
    # list comprehension aplica a cor correspondente a cada ação via ACTION_COLORS
    # -------------------------------------------------------------------------
    action_counts = df["action"].value_counts()  # contagem por verbo de ação
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
    domain_counts = df["domain"].value_counts()  # contagem por domínio
    fig.add_trace(
        go.Bar(
            x=domain_counts.values.tolist(), # eixo X: quantidade de commits
            y=domain_counts.index.tolist(),  # eixo Y: nomes dos domínios
            orientation="h",                 # barras na horizontal
            marker_color="#4B9EFF",          # azul uniforme para todos os domínios
            name="por domínio",
            hovertemplate="Domínio: %{y}<br>Commits: %{x}<extra></extra>",
        ),
        row=2, col=1  # posição na grade: linha 2, coluna 1
    )

    # -------------------------------------------------------------------------
    # Gráfico 4: Heatmap — commits por dia da semana vs semana
    # Estilo GitHub contributions: células mais escuras = mais commits
    #
    # groupby(["week","weekday"]).size() → conta commits por combinação semana+dia
    # unstack(fill_value=0)             → transforma weekday em colunas (pivot table)
    # reindex(WEEKDAY_ORDER)            → garante ordem Seg→Dom mesmo sem dados
    # sorted(heatmap_pivot.index)       → ordena as semanas cronologicamente
    # .values.T                         → transpõe: dias ficam no eixo Y, semanas no X
    # -------------------------------------------------------------------------
    heatmap_pivot = df.groupby(["week", "weekday"]).size().unstack(fill_value=0)
    heatmap_pivot = heatmap_pivot.reindex(columns=WEEKDAY_ORDER, fill_value=0)
    heatmap_pivot = heatmap_pivot.loc[sorted(heatmap_pivot.index)]
    fig.add_trace(
        go.Heatmap(
            z=heatmap_pivot.values.T.tolist(), # matriz de valores (dias × semanas)
            x=heatmap_pivot.index.tolist(),    # eixo X: semanas
            y=WEEKDAY_PT,                      # eixo Y: dias em português
            # colorscale: gradiente de cor proporcional à quantidade de commits
            # 0 commits → fundo escuro; máximo → verde
            colorscale=[
                [0.0,  "#0F1117"],   # 0 commits → cor de fundo (invisível)
                [0.01, "#1a2744"],   # 1 commit  → azul muito escuro
                [0.3,  "#1d4ed8"],   # poucos    → azul médio
                [0.6,  "#0ea5e9"],   # médio     → azul claro
                [1.0,  "#00C896"],   # máximo    → verde destaque
            ],
            showscale=True,  # exibe a barra de escala de cor à direita
            colorbar=dict(
                title=dict(text="commits", font=dict(color=TEXT_COLOR)),
                tickfont=dict(color=TEXT_COLOR),
                x=1.02,  # posição horizontal da barra (levemente fora do gráfico)
            ),
            hovertemplate="Semana: %{x}<br>Dia: %{y}<br>Commits: %{z}<extra></extra>",
            name="heatmap",
        ),
        row=2, col=2  # posição na grade: linha 2, coluna 2
    )

    # -------------------------------------------------------------------------
    # Cards de totais no topo via annotations
    # annotations são caixas de texto posicionadas livremente no canvas
    # xref/yref="paper" → coordenadas relativas ao canvas total (0.0 a 1.0)
    # y=1.08            → posiciona acima dos subplots (fora da área de plotagem)
    # -------------------------------------------------------------------------
    cards = [
        (f"{total_commits}", "Total de Commits", 0.12), # x=0.12 → canto esquerdo
        (first_commit,       "Primeiro Commit",  0.37), # x=0.37 → centro-esquerda
        (last_commit,        "Último Commit",    0.62), # x=0.62 → centro-direita
        (f"{total_labs}",    "Labs Realizados",  0.87), # x=0.87 → canto direito
    ]
    annotations = []
    for valor, label, x_pos in cards:
        annotations.append(dict(
            # HTML inline para formatar valor (grande, verde) e label (pequeno, cinza)
            text=(
                f"<b style='font-size:22px;color:#00C896'>{valor}</b><br>"
                f"<span style='font-size:11px;color:#94A3B8'>{label}</span>"
            ),
            x=x_pos, y=1.08,       # posição no canvas
            xref="paper", yref="paper",
            showarrow=False,        # sem seta apontando para algum ponto
            align="center",
            font=dict(family=FONT_FAMILY),
            bgcolor="#1E2130",      # fundo escuro do card
            bordercolor="#00C896", # borda verde
            borderwidth=1,
            borderpad=8,           # espaçamento interno do card
        ))
    # Preserva as annotations dos títulos dos subplots geradas pelo make_subplots
    # Sem isso, os títulos de cada gráfico desaparecem
    for ann in fig.layout.annotations:
        annotations.append(ann)

    # update_layout aplica configurações globais ao dashboard inteiro
    fig.update_layout(
        title=dict(
            text="📊 Git Log Dashboard — CCNP Enterprise Lab",
            font=dict(size=20, color=TEXT_COLOR, family=FONT_FAMILY),
            x=0.5,  # centraliza o título horizontalmente
        ),
        annotations=annotations,
        paper_bgcolor=BG_COLOR,  # cor de fundo externo (fora dos gráficos)
        plot_bgcolor=BG_COLOR,   # cor de fundo interno (área dos gráficos)
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=800,              # altura total do dashboard em pixels
        showlegend=False,        # oculta a legenda (não necessária aqui)
        margin=dict(t=140, b=60, l=60, r=60),  # margens: top maior para os cards
    )
    # Aplica grid escuro em todos os eixos X e Y de todos os subplots de uma vez
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    # write_html gera o arquivo HTML interativo com Plotly embutido
    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    fig.write_html(OUTPUT_HTML)
    print(f"[4/4] Dashboard salvo: {OUTPUT_HTML}")


# =============================================================================
# PONTO DE ENTRADA
# if __name__ == "__main__" garante que main() só executa quando o script
# é chamado diretamente — essencial para a futura modularização
# =============================================================================

def main():
    args = parse_args()  # lê e valida os argumentos da linha de comando
    # Cabeçalho visual para feedback no terminal
    print(f"\n{'='*55}")
    print(f"  Pipeline completo: git log → CSV → Dashboard")
    print(f"  Repositório: {args.repo}")
    print(f"{'='*55}\n")
    validate_repo(args.repo)              # valida antes de executar qualquer etapa
    lines   = extract_git_log(args.repo) # [1/4] Extração: git log → raw_git_log.txt
    records = parse_lines(lines)          # [2/4] Parsing: linhas → lista de dicionários
    save_csv(records)                     # [3/4] CSV: dicionários → git_log.csv
    build_dashboard()                     # [4/4] Dashboard: CSV → HTML interativo
    print(f"\n✓ Concluído! Abra: {OUTPUT_HTML}\n")


if __name__ == "__main__":
    main()