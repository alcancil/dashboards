# =============================================================================
# 15_dashboard_completo_commented.py
# Dashboard completo CCNP ENCORE 350-401 — script monolítico com 3 abas
#
# O que este script faz:
#   [1/4] EXTRAÇÃO    — executa git log no repositório CISCO e salva output bruto
#   [2/4] PARSING     — transforma linhas do git log em registros estruturados
#   [3/4] BLUEPRINT   — escaneia estrutura de pastas do CCNP via os.listdir()
#   [4/4] DASHBOARD   — gera HTML com 3 abas usando Plotly + HTML/CSS/JS
#
# Por que monolítico aqui?
#   Script 15 é a versão "tudo em um lugar" para entender o fluxo completo.
#   O script 16 será a versão modularizada — mesma lógica, código separado.
#   Essa progressão demonstra o princípio da responsabilidade única na prática.
#
# Novidades em relação aos scripts 13 e 14:
#   - Dois argumentos: --repo (git) e --ccnp (pasta do blueprint)
#   - Fonte de dados dupla: git log + estrutura de pastas (os.listdir)
#   - Dashboard com 3 abas: Resumo Geral, Progresso CCNP, Análise de Commits
#   - Abas implementadas com HTML/CSS/JS mínimo (não é uma lib externa)
#   - Gráficos Plotly embutidos via pio.to_html(full_html=False)
#   - Cards informativos em HTML puro (não via annotations do Plotly)
#   - Tabela de domínios em HTML puro na aba de progresso
#
# Uso:
#   python src/avancado/15_dashboard_completo.py \
#     --repo "D:\ESTUDOS\CISCO\CISCO" \
#     --ccnp "D:\ESTUDOS\CISCO\CISCO\CCNP 350-401 ENCOR"
# =============================================================================

import subprocess              # Executa comandos do sistema (git log)
import csv                     # Escrita de arquivos CSV estruturados
import os                      # Caminhos, listagem de diretórios
import argparse                # Argumentos de linha de comando com --help
from datetime import datetime  # Conversão e formatação de datas

import pandas as pd                        # Manipulação de dados tabulares
import plotly.graph_objects as go          # Criação de gráficos Plotly
from plotly.subplots import make_subplots  # Layout com múltiplos gráficos
import plotly.io as pio                    # Exportação de figuras para HTML


# =============================================================================
# CONSTANTES DE CONFIGURAÇÃO
# =============================================================================

# BASE_DIR: sobe 3 níveis a partir de src/avancado/ para chegar à raiz do projeto
#   src/avancado/ → (1) src/ → (2) DASHBOARDS/ (raiz)
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_RAW  = os.path.join(BASE_DIR, "data", "raw", "raw_git_log.txt")
OUTPUT_CSV  = os.path.join(BASE_DIR, "data", "processed", "git_log.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "docs", "15_dashboard_completo.html")

# Delimitador usado no git log --pretty=format
# Escolhemos "|" porque raramente aparece em mensagens de commit
DELIMITER = "|"

# Ordem fixa dos domínios do Blueprint ENCORE 350-401
# Usamos lista para garantir sempre a mesma sequência nos gráficos
DOMAIN_ORDER = [
    "01 - Architecture",
    "02 - Virtualization",
    "03 - Infrastructure",
    "04 - Network Assurance",
    "05 - Security",
    "06 - Automation",
]

# -----------------------------------------------------------------------------
# ACTION_MAP — normalização de verbos de ação dos commits
# Trata typos reais encontrados no repositório CISCO
# Ex: "alteradoo", "aletardo", "alterad" → todos viram "Alterado"
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# DOMAIN_KEYWORDS — identificação de domínio CCNP nas mensagens de commit
# Lista de tuplas (palavra-chave, domínio) percorrida em ordem
# Primeira correspondência vence — palavras específicas vêm antes das genéricas
# Operador 'in' faz busca de substring após converter mensagem para lowercase
# -----------------------------------------------------------------------------
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

# Cores para o gráfico de barras de ações
ACTION_COLORS = {
    "Alterado": "#4B9EFF", "Adicionado": "#00C896", "Ajustado": "#FB923C",
    "Acertado": "#A78BFA", "Removido": "#FF4B4B", "Realizado": "#FACC15",
    "Separado": "#94A3B8", "Dividido": "#94A3B8", "Criado": "#34D399",
    "Corrigido": "#F472B6", "Atualizado": "#60A5FA", "Renomeado": "#CBD5E1",
    "Teste": "#FCD34D", "Outro": "#475569",
}

# Cor de destaque para cada domínio do Blueprint — usada em gráficos e tabela
DOMAIN_COLORS = {
    "01 - Architecture":      "#00C896",  # verde
    "02 - Virtualization":    "#4B9EFF",  # azul
    "03 - Infrastructure":    "#FB923C",  # laranja
    "04 - Network Assurance": "#A78BFA",  # roxo
    "05 - Security":          "#FF4B4B",  # vermelho
    "06 - Automation":        "#FACC15",  # amarelo
}

# Ordem e tradução dos dias da semana para o heatmap
WEEKDAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
WEEKDAY_PT    = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]

# Tema visual — estilo terminal escuro (padrão do projeto)
BG_COLOR    = "#0F1117"  # fundo principal
GRID_COLOR  = "#1E2130"  # linhas de grade e bordas
TEXT_COLOR  = "#E2E8F0"  # texto principal
ACCENT      = "#00C896"  # cor de destaque (verde)
FONT_FAMILY = "Courier New, monospace"


# =============================================================================
# ARGUMENTOS DE LINHA DE COMANDO
# =============================================================================

def parse_args():
    # RawTextHelpFormatter preserva quebras de linha no texto do --help
    parser = argparse.ArgumentParser(
        description="Dashboard completo CCNP — 3 abas: Resumo, Progresso e Git Log.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # --repo: raiz do repositório Git (onde está a pasta .git)
    parser.add_argument(
        "--repo",
        required=True,
        metavar="REPO",
        help="Caminho para a raiz do repositório Git\nEx: D:\\ESTUDOS\\CISCO\\CISCO"
    )
    # --ccnp: pasta raiz do blueprint ENCORE (onde estão os 6 domínios)
    parser.add_argument(
        "--ccnp",
        required=True,
        metavar="CCNP",
        help="Caminho para a pasta do Blueprint CCNP ENCOR\nEx: D:\\ESTUDOS\\CISCO\\CISCO\\CCNP 350-401 ENCOR"
    )
    # parse_args() lê sys.argv e retorna namespace com args.repo e args.ccnp
    return parser.parse_args()


def validate_paths(repo_path, ccnp_path):
    # Fail fast: valida tudo antes de executar qualquer etapa
    # os.path.isdir verifica se o caminho existe e é um diretório
    if not os.path.isdir(repo_path):
        raise FileNotFoundError(f"Repositório não encontrado: {repo_path}")
    # Todo repositório Git tem uma pasta oculta .git na raiz
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        raise ValueError(f"Não é um repositório Git: {repo_path}")
    # Verifica se a pasta do blueprint existe
    if not os.path.isdir(ccnp_path):
        raise FileNotFoundError(f"Pasta CCNP não encontrada: {ccnp_path}")


# =============================================================================
# ETAPA 1 — EXTRAÇÃO DO GIT LOG
# Executa git log no repositório e retorna lista de linhas brutas
# Salva também em data/raw/raw_git_log.txt como fonte da verdade
# =============================================================================

def extract_git_log(repo_path):
    # exist_ok=True evita erro se o diretório já existir
    os.makedirs(os.path.dirname(OUTPUT_RAW), exist_ok=True)

    # subprocess.run executa o git log como se fosse no terminal
    # cwd=repo_path    → muda o diretório de trabalho para o repositório
    # capture_output   → captura stdout e stderr sem imprimir no terminal
    # text=True        → decodifica bytes para string automaticamente
    # encoding="utf-8" → necessário para commits com caracteres especiais (ç, ã)
    result = subprocess.run(
        ["git", "log", f"--pretty=format:%H{DELIMITER}%ad{DELIMITER}%s", "--date=iso"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    # returncode != 0 indica erro na execução do git
    if result.returncode != 0:
        raise RuntimeError(f"Erro ao executar git log: {result.stderr}")

    # Salva output bruto — nunca editar manualmente
    with open(OUTPUT_RAW, "w", encoding="utf-8") as f:
        f.write(result.stdout)

    # splitlines() divide em lista de linhas; filtro remove linhas vazias
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    print(f"[1/4] Git log extraído: {len(lines)} commits")
    return lines


# =============================================================================
# ETAPA 2 — PARSING DO GIT LOG
# Funções auxiliares de extração + função principal parse_lines()
# Filosofia: sem regex — apenas split(), strip(), lower() e operador 'in'
# =============================================================================

def extract_action(message):
    # Pega a primeira palavra da mensagem e busca no dicionário ACTION_MAP
    # Se não encontrar, retorna "Outro" como valor padrão
    first_word = message.strip().split()[0].lower() if message.strip() else ""
    return ACTION_MAP.get(first_word, "Outro")


def extract_domain_from_commit(message):
    # Converte a mensagem para lowercase e verifica se alguma
    # palavra-chave de DOMAIN_KEYWORDS está contida nela
    # A primeira correspondência vence (ordem da lista importa)
    msg_lower = message.lower()
    for keyword, domain in DOMAIN_KEYWORDS:
        if keyword in msg_lower:
            return domain
    return "Geral"  # nenhuma palavra-chave encontrada


def extract_lab(message):
    # Detecta commits de laboratório pela presença de "Exemplo Prático"
    # na mensagem — padrão usado para nomear pastas de lab no repositório CISCO
    # Aceita com e sem acento para robustez
    msg_lower = message.lower()
    return "Sim" if "exemplo prático" in msg_lower or "exemplo pratico" in msg_lower else "Não"


def parse_lines(lines):
    records = []  # lista que acumula dicionários de cada commit

    for line in lines:
        # maxsplit=2 garante que "|" no texto da mensagem não quebre o parse
        parts = line.split(DELIMITER, maxsplit=2)
        if len(parts) != 3:
            continue  # descarta linhas com formato inesperado

        # Desempacota os 3 campos: hash do commit, data ISO, mensagem
        commit_hash, date_str, message = parts

        try:
            # --date=iso gera: "2026-02-26 10:30:00 -0300"
            # [:19] pega só "2026-02-26 10:30:00" — descarta o timezone
            dt = datetime.fromisoformat(date_str.strip()[:19])
        except ValueError:
            continue  # descarta registros com data inválida

        records.append({
            "hash":    commit_hash.strip(),
            "date":    dt.strftime("%Y-%m-%d"),  # Ex: 2026-02-26
            "week":    dt.strftime("%Y-W%W"),     # Ex: 2026-W08 (agrupamento semanal)
            "weekday": dt.strftime("%A"),         # Ex: Thursday (para heatmap)
            "message": message.strip(),
            "action":  extract_action(message),            # Ex: Adicionado
            "domain":  extract_domain_from_commit(message),# Ex: Infrastructure
            "lab":     extract_lab(message),               # Ex: Sim ou Não
        })

    print(f"[2/4] Parsing concluído: {len(records)} registros")
    return records


def save_csv(records):
    # exist_ok=True evita erro se o diretório já existir
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    fieldnames = ["hash","date","week","weekday","message","action","domain","lab"]
    # newline="" evita linhas em branco extras no Windows
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()       # linha de cabeçalho com nomes das colunas
        writer.writerows(records)  # todos os registros de uma vez
    print(f"[3/4] CSV salvo: {OUTPUT_CSV}")


# =============================================================================
# ETAPA 3 — LEITURA DA ESTRUTURA DE PASTAS DO BLUEPRINT
#
# Diferença fundamental em relação aos scripts 13 e 14:
#   Antes: só analisávamos commits (o que e quando você commitou)
#   Agora: também analisamos a estrutura de pastas (o que você criou/estudou)
#
# Estrutura esperada:
#   ccnp_path/
#   ├── 01 - Architecture/
#   │   ├── 01 - QoS/
#   │   │   ├── 01 - Limite de Banda - Policing/   ← subtópico
#   │   │   ├── 10 - Exemplo Prático de QoS/       ← subtópico + lab
#   │   │   └── Arquivos/                          ← ignorado
#   │   └── 02 - Processo de Encaminhamento/
#   └── 02 - Virtualization/
#
# O que a função coleta por domínio:
#   topics          → dicionário de tópicos com seus subtópicos e labs
#   total_subtopics → contagem total de subtópicos (exclui Arquivos/Imagens/Simulado)
#   total_labs      → contagem de pastas com "Exemplo Pr" no nome
# =============================================================================

def scan_blueprint(ccnp_path):
    domains = {}  # dicionário indexado pelo nome do domínio

    for domain_name in DOMAIN_ORDER:
        domain_path = os.path.join(ccnp_path, domain_name)

        # Se o domínio não existe no disco, registra como vazio (ex: 04, 05)
        if not os.path.isdir(domain_path):
            domains[domain_name] = {"topics": {}, "total_subtopics": 0, "total_labs": 0}
            continue

        topics = {}
        # sorted() garante ordem alfabética/numérica independente do OS
        for topic in sorted(os.listdir(domain_path)):
            topic_path = os.path.join(domain_path, topic)
            if not os.path.isdir(topic_path):
                continue  # ignora arquivos soltos dentro do domínio

            subtopics = []
            labs      = []

            for sub in sorted(os.listdir(topic_path)):
                sub_path = os.path.join(topic_path, sub)
                if not os.path.isdir(sub_path):
                    continue  # ignora arquivos

                # Pastas de suporte não são subtópicos de estudo — ignora
                if sub in ("Arquivos", "Imagens", "Simulado"):
                    continue

                subtopics.append(sub)

                # Detecta labs pela presença de "Exemplo Pr" no nome da pasta
                # Cobre: "Exemplo Prático", "Exemplo Pratico", "Exemplo Prßtico" (encoding)
                if "exemplo pr" in sub.lower() or "exemplo pratico" in sub.lower():
                    labs.append(sub)

            topics[topic] = {"subtopics": subtopics, "labs": labs}

        # sum() com generator expression soma os subtópicos de todos os tópicos
        total_subtopics = sum(len(v["subtopics"]) for v in topics.values())
        total_labs      = sum(len(v["labs"])      for v in topics.values())

        domains[domain_name] = {
            "topics":          topics,
            "total_subtopics": total_subtopics,
            "total_labs":      total_labs,
        }

    print(f"[4/4] Blueprint escaneado: {len(domains)} domínios")
    return domains


# =============================================================================
# DASHBOARD — ABA 1: RESUMO GERAL
#
# Combina dados do git log (commits) + estrutura de pastas (subtópicos/labs)
# Mostra visão executiva do progresso de estudos
#
# Contém:
#   - 4 cards informativos em HTML puro (não via annotations Plotly)
#   - Gráfico de barras horizontais: subtópicos por domínio
#   - Gráfico de linha: commits ao longo do tempo
#
# Retorna: string HTML com cards + gráfico Plotly embutido
# =============================================================================

def build_aba_resumo(domains, df):
    # Agrega métricas de todos os domínios
    total_subtopics    = sum(d["total_subtopics"] for d in domains.values())
    total_labs         = sum(d["total_labs"]      for d in domains.values())
    # sum(1 for ...) conta domínios com pelo menos 1 subtópico
    dominios_iniciados = sum(1 for d in domains.values() if d["total_subtopics"] > 0)
    total_commits      = len(df)

    # Prepara listas paralelas para os gráficos — mesma ordem = DOMAIN_ORDER
    # replace() remove o prefixo numérico ("01 - ") para exibição limpa
    dom_names  = [d.replace("01 - ","").replace("02 - ","").replace("03 - ","")
                   .replace("04 - ","").replace("05 - ","").replace("06 - ","")
                  for d in DOMAIN_ORDER]
    dom_subs   = [domains[d]["total_subtopics"] for d in DOMAIN_ORDER]
    dom_colors = [DOMAIN_COLORS[d] for d in DOMAIN_ORDER]

    # make_subplots com 1 linha e 2 colunas — layout lado a lado
    fig1 = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Subtópicos estudados por domínio", "Commits ao longo do tempo"),
        horizontal_spacing=0.12,
    )

    # Barras horizontais: subtópicos por domínio com cor do domínio
    fig1.add_trace(
        go.Bar(
            x=dom_subs,       # eixo X: quantidade de subtópicos
            y=dom_names,      # eixo Y: nome do domínio
            orientation="h",  # horizontal
            marker_color=dom_colors,
            name="Subtópicos",
            hovertemplate="Domínio: %{y}<br>Subtópicos: %{x}<extra></extra>",
        ),
        row=1, col=1
    )

    # Linha de commits por semana com área preenchida
    commits_by_week = df.groupby("week").size().reset_index(name="count").sort_values("week")
    fig1.add_trace(
        go.Scatter(
            x=commits_by_week["week"],
            y=commits_by_week["count"],
            mode="lines+markers",
            line=dict(color=ACCENT, width=2),
            marker=dict(size=5, color=ACCENT),
            fill="tozeroy",                      # área preenchida até zero
            fillcolor="rgba(0,200,150,0.1)",     # verde com transparência
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

    # Cards em HTML puro — mais flexíveis que annotations Plotly para layout
    # display:flex com gap cria linha de cards responsiva
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

    # pio.to_html(full_html=False) retorna só o <div> do gráfico — sem <html>, <head> etc.
    # include_plotlyjs=False porque o JS do Plotly já está carregado no HTML principal
    graph_html = pio.to_html(fig1, full_html=False, include_plotlyjs=False)
    return cards_html + graph_html  # concatena cards + gráfico


# =============================================================================
# DASHBOARD — ABA 2: PROGRESSO POR DOMÍNIO
#
# Foco na estrutura de pastas — mostra o que foi criado/estudado
#
# Contém:
#   - Barras agrupadas: subtópicos vs labs por domínio (comparação)
#   - Pizza (donut): distribuição percentual de subtópicos entre domínios
#   - Tabela HTML: resumo detalhado de tópicos, subtópicos, labs e status
#
# Retorna: string HTML com gráfico Plotly + tabela HTML
# =============================================================================

def build_aba_progresso(domains):
    # split(" - ", 1)[1] remove o prefixo numérico e pega só o nome do domínio
    # maxsplit=1 garante que só o primeiro " - " é separado
    dom_names  = [d.split(" - ", 1)[1] for d in DOMAIN_ORDER]
    dom_subs   = [domains[d]["total_subtopics"] for d in DOMAIN_ORDER]
    dom_labs   = [domains[d]["total_labs"]      for d in DOMAIN_ORDER]
    dom_colors = [DOMAIN_COLORS[d]             for d in DOMAIN_ORDER]

    # specs=[[ {"type":"xy"}, {"type":"domain"} ]] é obrigatório quando misturamos
    # gráfico cartesiano (Bar) com gráfico polar/circular (Pie) no mesmo subplot
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Subtópicos vs Labs por domínio", "Distribuição de subtópicos"),
        specs=[[{"type": "xy"}, {"type": "domain"}]],
        horizontal_spacing=0.12,
    )

    # Barras agrupadas — subtópicos com cor do domínio
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
    # Barras de labs em vermelho semitransparente para contraste visual
    fig.add_trace(
        go.Bar(
            name="Labs",
            x=dom_names,
            y=dom_labs,
            marker_color=["rgba(255,75,75,0.8)"] * 6,  # vermelho para todos os 6 domínios
            hovertemplate="Domínio: %{x}<br>Labs: %{y}<extra></extra>",
        ),
        row=1, col=1
    )

    # Pizza (donut) de distribuição — hole=0.4 cria o buraco central
    # Domínios com 0 subtópicos aparecem como fatia vazia (não somem)
    fig.add_trace(
        go.Pie(
            labels=dom_names,
            values=dom_subs,
            marker_colors=dom_colors,
            hole=0.4,  # transforma pizza em donut
            hovertemplate="Domínio: %{label}<br>Subtópicos: %{value}<br>(%{percent})<extra></extra>",
        ),
        row=1, col=2
    )

    fig.update_layout(
        paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=420,
        barmode="group",  # barras lado a lado (não empilhadas)
        legend=dict(bgcolor=BG_COLOR, bordercolor=GRID_COLOR, borderwidth=1),
        margin=dict(t=50, b=40, l=10, r=10),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    # Tabela HTML de detalhes por domínio
    # Construída com string concatenation para não depender de lib extra
    table_rows = ""
    for domain in DOMAIN_ORDER:
        d      = domains[domain]
        name   = domain.split(" - ", 1)[1]   # remove prefixo numérico
        subs   = d["total_subtopics"]
        labs   = d["total_labs"]
        tops   = len(d["topics"])             # quantidade de tópicos do domínio
        color  = DOMAIN_COLORS[domain]
        # Status visual: ✅ se tem subtópicos, ⏳ se ainda não iniciou
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
    return graph_html + table_html  # gráfico primeiro, tabela embaixo


# =============================================================================
# DASHBOARD — ABA 3: ANÁLISE DE COMMITS
#
# Foco nos dados do git log — quando e como você trabalhou
# Idêntica ao dashboard dos scripts 13 e 14, mas integrada como aba
#
# Contém:
#   - 4 cards: total commits, primeiro/último commit, labs nos commits
#   - Linha: commits ao longo do tempo (por semana)
#   - Barras: distribuição por ação (verbo normalizado)
#   - Barras horizontais: distribuição por domínio detectado nos commits
#   - Heatmap: commits por dia da semana vs semana (estilo GitHub contributions)
#
# Retorna: string HTML com cards + gráfico Plotly 2x2
# =============================================================================

def build_aba_commits(df):
    # make_subplots 2x2 — grade de 4 gráficos
    # vertical_spacing e horizontal_spacing controlam o espaço entre eles
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

    # [1,1] Linha com área — commits por semana
    commits_by_week = df.groupby("week").size().reset_index(name="count").sort_values("week")
    fig.add_trace(
        go.Scatter(
            x=commits_by_week["week"],
            y=commits_by_week["count"],
            mode="lines+markers",
            line=dict(color=ACCENT, width=2),
            marker=dict(size=5, color=ACCENT),
            fill="tozeroy",                     # área preenchida até zero
            fillcolor="rgba(0,200,150,0.1)",
            hovertemplate="Semana: %{x}<br>Commits: %{y}<extra></extra>",
        ), row=1, col=1
    )

    # [1,2] Barras — distribuição por ação com cor por tipo
    action_counts = df["action"].value_counts()  # ordena do mais ao menos frequente
    fig.add_trace(
        go.Bar(
            x=action_counts.index.tolist(),
            y=action_counts.values.tolist(),
            # list comprehension busca a cor de cada ação; "#475569" como fallback
            marker_color=[ACTION_COLORS.get(a, "#475569") for a in action_counts.index],
            hovertemplate="Ação: %{x}<br>Commits: %{y}<extra></extra>",
        ), row=1, col=2
    )

    # [2,1] Barras horizontais — distribuição por domínio detectado nos commits
    domain_counts = df["domain"].value_counts()
    fig.add_trace(
        go.Bar(
            x=domain_counts.values.tolist(),  # eixo X: quantidade
            y=domain_counts.index.tolist(),   # eixo Y: nome do domínio
            orientation="h",                  # horizontal
            marker_color="#4B9EFF",
            hovertemplate="Domínio: %{y}<br>Commits: %{x}<extra></extra>",
        ), row=2, col=1
    )

    # [2,2] Heatmap — estilo GitHub contributions
    # groupby + unstack cria pivot table: linhas=semanas, colunas=dias
    heatmap_pivot = df.groupby(["week","weekday"]).size().unstack(fill_value=0)
    # reindex garante que todos os dias apareçam mesmo sem dados
    heatmap_pivot = heatmap_pivot.reindex(columns=WEEKDAY_ORDER, fill_value=0)
    # sorted() garante ordem cronológica das semanas
    heatmap_pivot = heatmap_pivot.loc[sorted(heatmap_pivot.index)]
    fig.add_trace(
        go.Heatmap(
            z=heatmap_pivot.values.T.tolist(),  # .T transpõe: dias no Y, semanas no X
            x=heatmap_pivot.index.tolist(),     # eixo X: semanas
            y=WEEKDAY_PT,                       # eixo Y: dias em português
            colorscale=[
                [0.0,  "#0F1117"],  # 0 commits → fundo escuro (invisível)
                [0.01, "#1a2744"],  # 1 commit  → azul muito escuro
                [0.3,  "#1d4ed8"],  # poucos    → azul médio
                [0.6,  "#0ea5e9"],  # médio     → azul claro
                [1.0,  ACCENT],     # máximo    → verde destaque
            ],
            showscale=True,
            colorbar=dict(
                title=dict(text="commits", font=dict(color=TEXT_COLOR)),
                tickfont=dict(color=TEXT_COLOR),
                x=1.02,  # posiciona barra de escala fora do gráfico
            ),
            hovertemplate="Semana: %{x}<br>Dia: %{y}<br>Commits: %{z}<extra></extra>",
        ), row=2, col=2
    )

    fig.update_layout(
        paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=700, showlegend=False,
        margin=dict(t=50, b=40, l=10, r=60),  # r=60 para acomodar colorbar
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    # Métricas para os cards desta aba
    total_commits = len(df)
    total_labs    = (df["lab"] == "Sim").sum()           # boolean mask → contagem
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
# MONTAGEM DO HTML FINAL COM AS 3 ABAS
#
# Estratégia: cada aba é um <div> com display:none por padrão
# A função showTab() em JavaScript alterna qual div fica visível
#
# Por que não usar uma lib de tabs (Bootstrap, etc.)?
#   Porque o objetivo é manter o HTML gerado sem dependências externas além
#   do próprio Plotly — que já carregamos via CDN para os gráficos.
#
# include_plotlyjs=False em pio.to_html() evita que o JS do Plotly seja
# embutido N vezes (uma por figura) — carregamos uma vez só no <head>
# =============================================================================

def build_html(aba1_html, aba2_html, aba3_html):
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard CCNP ENCORE 350-401</title>
  <!-- Plotly carregado uma única vez via CDN — compartilhado por todas as abas -->
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    /* Reset básico para consistência entre browsers */
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
    /* Container das abas — display:flex coloca botões lado a lado */
    .tabs {{
      display: flex;
      gap: 4px;
      margin-bottom: 20px;
      border-bottom: 2px solid {GRID_COLOR};
    }}
    /* Botão de aba inativo */
    .tab-btn {{
      padding: 10px 24px;
      background: {GRID_COLOR};
      color: #94A3B8;
      border: none;
      cursor: pointer;
      font-family: {FONT_FAMILY};
      font-size: 14px;
      border-radius: 6px 6px 0 0;  /* arredonda só os cantos superiores */
      transition: all 0.2s;
    }}
    .tab-btn:hover {{ background: #2a3050; color: {TEXT_COLOR}; }}
    /* Botão ativo: borda verde, fundo do body, margem negativa para "grudar" na linha */
    .tab-btn.active {{
      background: {BG_COLOR};
      color: {ACCENT};
      border: 2px solid {ACCENT};
      border-bottom: 2px solid {BG_COLOR};  /* esconde borda inferior sobre a linha */
      margin-bottom: -2px;                  /* sobe 2px para cobrir a border-bottom do .tabs */
    }}
    /* Conteúdo de cada aba: oculto por padrão, visível quando tem classe .active */
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; }}
  </style>
</head>
<body>
  <h1>📊 Dashboard CCNP ENCORE 350-401</h1>
  <p class="subtitle">Progresso de estudos — estrutura de pastas + análise de commits</p>

  <!-- Barra de abas: cada botão chama showTab() com o id do conteúdo -->
  <div class="tabs">
    <button class="tab-btn active" onclick="showTab('resumo')">🏠 Resumo Geral</button>
    <button class="tab-btn" onclick="showTab('progresso')">📈 Progresso CCNP</button>
    <button class="tab-btn" onclick="showTab('commits')">🔍 Análise de Commits</button>
  </div>

  <!-- Conteúdo de cada aba — HTML gerado pelo Python é injetado aqui -->
  <div id="resumo" class="tab-content active">{aba1_html}</div>
  <div id="progresso" class="tab-content">{aba2_html}</div>
  <div id="commits" class="tab-content">{aba3_html}</div>

  <script>
    function showTab(name) {{
      // Remove .active de todos os conteúdos e botões
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
      // Ativa o conteúdo e o botão correspondente ao nome clicado
      document.getElementById(name).classList.add('active');
      event.target.classList.add('active');
    }}
  </script>
</body>
</html>"""
    return html


# =============================================================================
# MAIN — Orquestrador principal
# Executa todas as etapas em sequência e gera o HTML final
# =============================================================================

def main():
    args = parse_args()  # lê e valida os argumentos da linha de comando
    print(f"\n{'='*55}")
    print(f"  Dashboard Completo — CCNP ENCORE 350-401")
    print(f"  Repositório : {args.repo}")
    print(f"  Blueprint   : {args.ccnp}")
    print(f"{'='*55}\n")

    validate_paths(args.repo, args.ccnp)  # fail fast antes de qualquer processamento

    # Pipeline de dados: git log → parsing → CSV → DataFrame
    lines   = extract_git_log(args.repo)   # [1/4] extração
    records = parse_lines(lines)            # [2/4] parsing
    save_csv(records)                       # salva CSV atualizado
    # Lê o CSV como DataFrame para uso nos gráficos
    df      = pd.read_csv(OUTPUT_CSV, parse_dates=["date"])

    # Escaneia a estrutura de pastas do blueprint CCNP
    domains = scan_blueprint(args.ccnp)    # [3/4] blueprint

    # Gera o HTML de cada aba separadamente
    print("Gerando dashboard...")
    aba1 = build_aba_resumo(domains, df)   # combina pastas + commits
    aba2 = build_aba_progresso(domains)    # só estrutura de pastas
    aba3 = build_aba_commits(df)           # só commits

    # Monta e salva o HTML final com as 3 abas
    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(build_html(aba1, aba2, aba3))

    print(f"\n✓ Concluído! Abra: {OUTPUT_HTML}\n")


# if __name__ == "__main__" garante que main() só executa quando o script
# é chamado diretamente — não quando importado como módulo por outro script
if __name__ == "__main__":
    main()