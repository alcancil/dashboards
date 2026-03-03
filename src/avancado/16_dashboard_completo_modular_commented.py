# =============================================================================
# 16_dashboard_completo_modular_commented.py
# Dashboard completo CCNP ENCORE 350-401 — versao modular
#
# Diferenca em relacao ao script 15 (monolitico):
#   Antes: extract_git_log, parse_lines, save_csv e scan_blueprint dentro do script
#   Agora: essas funcoes vivem em modulos proprios e sao importadas aqui
#
# Modulos importados:
#   scripts/parsing/git_log/extract.py   → validate_repo, extract_git_log
#   scripts/parsing/git_log/parser.py    → parse_lines, save_csv
#   scripts/parsing/blueprint/scanner.py → scan_blueprint, DOMAIN_ORDER, DOMAIN_COLORS
#
# O que fica no orquestrador:
#   - parse_args()         → argumentos CLI
#   - validate_ccnp()      → validacao da pasta do blueprint
#   - build_aba_resumo()   → grafico da aba 1
#   - build_aba_progresso()→ grafico da aba 2
#   - build_aba_commits()  → grafico da aba 3
#   - build_html()         → monta HTML final com abas
#   - main()               → orquestra tudo
#
# Narrativa do portfolio:
#   Script 15 → monolitico: tudo em um lugar para entender o fluxo
#   Script 16 → modular: responsabilidades separadas, codigo reutilizavel
#   A logica de negocio nao mudou — so a organizacao mudou.
#
# Uso:
#   python src/avancado/16_dashboard_completo_modular.py \
#     --repo "D:\ESTUDOS\CISCO\CISCO" \
#     --ccnp "D:\ESTUDOS\CISCO\CISCO\CCNP 350-401 ENCOR"
# =============================================================================

import argparse   # Argumentos de linha de comando com --help automatico
import os         # Manipulacao de caminhos portaveis
import sys        # Manipulacao do sys.path para importacao de modulos

import pandas as pd                        # Manipulacao de dados tabulares
import plotly.graph_objects as go          # Criacao de graficos Plotly
from plotly.subplots import make_subplots  # Layout com multiplos graficos
import plotly.io as pio                    # Exportacao de figuras para HTML


# BASE_DIR: sobe 3 niveis a partir de src/avancado/ para chegar a raiz do projeto
#   src/avancado/ → (1) src/ → (2) DASHBOARDS/ (raiz)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# sys.path.insert(0, BASE_DIR) adiciona a raiz do projeto ao inicio do sys.path
# Sem isso, o Python nao encontraria o pacote scripts/ como modulo importavel
sys.path.insert(0, BASE_DIR)

# Importa funcoes dos modulos — cada modulo tem responsabilidade unica
# extract.py  → I/O com o git (extrai e valida)
# parser.py   → transformacao dos dados brutos em registros estruturados
# scanner.py  → leitura da estrutura de pastas do blueprint
from scripts.parsing.git_log.extract   import validate_repo, extract_git_log
from scripts.parsing.git_log.parser    import parse_lines, save_csv
from scripts.parsing.blueprint.scanner import scan_blueprint, DOMAIN_ORDER, DOMAIN_COLORS
# DOMAIN_ORDER e DOMAIN_COLORS vem do scanner pois estao relacionados ao blueprint
# Centralizar la evita duplicar esses dados aqui no orquestrador


OUTPUT_CSV  = os.path.join(BASE_DIR, "data", "processed", "git_log.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "docs", "16_dashboard_completo_modular.html")

# Cores para o grafico de acoes — permanece no orquestrador pois e visual
ACTION_COLORS = {
    "Alterado": "#4B9EFF", "Adicionado": "#00C896", "Ajustado": "#FB923C",
    "Acertado": "#A78BFA", "Removido":   "#FF4B4B", "Realizado": "#FACC15",
    "Separado": "#94A3B8", "Dividido":   "#94A3B8", "Criado":    "#34D399",
    "Corrigido":"#F472B6", "Atualizado": "#60A5FA", "Renomeado": "#CBD5E1",
    "Teste":    "#FCD34D", "Outro":      "#475569",
}

# Ordem e traducao dos dias da semana para o heatmap
WEEKDAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
WEEKDAY_PT    = ["Seg","Ter","Qua","Qui","Sex","Sab","Dom"]

# Tema visual — identico ao script 15 para consistencia
BG_COLOR    = "#0F1117"
GRID_COLOR  = "#1E2130"
TEXT_COLOR  = "#E2E8F0"
ACCENT      = "#00C896"
FONT_FAMILY = "Courier New, monospace"


# =============================================================================
# ARGUMENTOS DE LINHA DE COMANDO
# =============================================================================

def parse_args():
    # Dois argumentos obrigatorios: --repo e --ccnp
    # --repo: raiz do repositorio Git (onde esta a pasta .git)
    # --ccnp: pasta raiz do blueprint ENCORE (onde estao os 6 dominios)
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
    # validate_repo() ja existe no modulo extract.py e e importada diretamente
    # validate_ccnp() fica aqui pois e especifica do orquestrador — nao pertence ao scanner
    if not os.path.isdir(ccnp_path):
        raise FileNotFoundError(f"Pasta CCNP nao encontrada: {ccnp_path}")


# =============================================================================
# ABA 1 — RESUMO GERAL
# Combina dados do git log (commits) + estrutura de pastas (subtopicos/labs)
# Visao executiva do progresso de estudos
# =============================================================================

def build_aba_resumo(domains, df):
    # Agrega metricas de todos os dominios via generator expression
    total_subtopics    = sum(d["total_subtopics"] for d in domains.values())
    total_labs         = sum(d["total_labs"]      for d in domains.values())
    dominios_iniciados = sum(1 for d in domains.values() if d["total_subtopics"] > 0)
    total_commits      = len(df)

    # split(" - ", 1)[1] remove o prefixo numerico — maxsplit=1 garante seguranca
    dom_names  = [d.split(" - ", 1)[1] for d in DOMAIN_ORDER]
    dom_subs   = [domains[d]["total_subtopics"] for d in DOMAIN_ORDER]
    # DOMAIN_COLORS importado do scanner — nao duplicado aqui
    dom_colors = [DOMAIN_COLORS[d] for d in DOMAIN_ORDER]

    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Subtopicos por dominio", "Commits ao longo do tempo"),
        horizontal_spacing=0.12)

    # Barras horizontais: subtopicos por dominio com cor do dominio
    fig.add_trace(go.Bar(x=dom_subs, y=dom_names, orientation="h",
        marker_color=dom_colors,
        hovertemplate="Dominio: %{y}<br>Subtopicos: %{x}<extra></extra>"), row=1, col=1)

    # Linha de commits por semana com area preenchida
    # groupby("week").size() conta commits por semana
    # reset_index(name="count") transforma em DataFrame com coluna "count"
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

    # Cards em HTML puro — display:flex cria linha responsiva de cards
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

    # pio.to_html(full_html=False) retorna so o <div> do grafico
    # include_plotlyjs=False porque o JS ja e carregado uma vez no <head>
    return cards + pio.to_html(fig, full_html=False, include_plotlyjs=False)


# =============================================================================
# ABA 2 — PROGRESSO POR DOMINIO
# Foco na estrutura de pastas — o que foi criado/estudado
# =============================================================================

def build_aba_progresso(domains):
    dom_names  = [d.split(" - ", 1)[1] for d in DOMAIN_ORDER]
    dom_subs   = [domains[d]["total_subtopics"] for d in DOMAIN_ORDER]
    dom_labs   = [domains[d]["total_labs"]      for d in DOMAIN_ORDER]
    dom_colors = [DOMAIN_COLORS[d]             for d in DOMAIN_ORDER]

    # specs obrigatorio ao misturar grafico cartesiano (Bar) com Pie no mesmo subplot
    fig = make_subplots(rows=1, cols=2,
        subplot_titles=("Subtopicos vs Labs por dominio", "Distribuicao de subtopicos"),
        specs=[[{"type":"xy"},{"type":"domain"}]], horizontal_spacing=0.12)

    # Barras agrupadas: subtopicos (cor do dominio) e labs (vermelho)
    fig.add_trace(go.Bar(name="Subtopicos", x=dom_names, y=dom_subs,
        marker_color=dom_colors,
        hovertemplate="Dominio: %{x}<br>Subtopicos: %{y}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Bar(name="Labs", x=dom_names, y=dom_labs,
        marker_color=["rgba(255,75,75,0.8)"]*6,
        hovertemplate="Dominio: %{x}<br>Labs: %{y}<extra></extra>"), row=1, col=1)

    # Pizza donut: hole=0.4 cria o buraco central
    fig.add_trace(go.Pie(labels=dom_names, values=dom_subs,
        marker_colors=dom_colors, hole=0.4,
        hovertemplate="Dominio: %{label}<br>Subtopicos: %{value}<br>(%{percent})<extra></extra>"),
        row=1, col=2)

    fig.update_layout(paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY), height=420,
        barmode="group",  # barras lado a lado, nao empilhadas
        legend=dict(bgcolor=BG_COLOR, bordercolor=GRID_COLOR, borderwidth=1),
        margin=dict(t=50, b=40, l=10, r=10))
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    # Tabela HTML de detalhes — construida por concatenacao de string
    rows = ""
    for domain in DOMAIN_ORDER:
        d      = domains[domain]
        name   = domain.split(" - ", 1)[1]
        subs   = d["total_subtopics"]
        labs   = d["total_labs"]
        tops   = len(d["topics"])        # quantidade de topicos do dominio
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

    # Grafico primeiro, tabela embaixo
    return pio.to_html(fig, full_html=False, include_plotlyjs=False) + table


# =============================================================================
# ABA 3 — ANALISE DE COMMITS
# Identica ao dashboard dos scripts 13/14/15 — integrada como aba
# Grade 2x2: linha, barras por acao, barras por dominio, heatmap
# =============================================================================

def build_aba_commits(df):
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=("Commits ao longo do tempo", "Distribuicao por acao",
                        "Distribuicao por dominio", "Heatmap dia vs semana"),
        vertical_spacing=0.18, horizontal_spacing=0.12,
        specs=[[{"type":"xy"},{"type":"xy"}],[{"type":"xy"},{"type":"xy"}]])

    # [1,1] Linha com area — commits por semana
    cwk = df.groupby("week").size().reset_index(name="count").sort_values("week")
    fig.add_trace(go.Scatter(x=cwk["week"], y=cwk["count"], mode="lines+markers",
        line=dict(color=ACCENT, width=2), marker=dict(size=5, color=ACCENT),
        fill="tozeroy", fillcolor="rgba(0,200,150,0.1)",
        hovertemplate="Semana: %{x}<br>Commits: %{y}<extra></extra>"), row=1, col=1)

    # [1,2] Barras — distribuicao por acao com cor por tipo
    ac = df["action"].value_counts()
    fig.add_trace(go.Bar(x=ac.index.tolist(), y=ac.values.tolist(),
        # list comprehension busca cor; "#475569" como fallback para acoes desconhecidas
        marker_color=[ACTION_COLORS.get(a, "#475569") for a in ac.index],
        hovertemplate="Acao: %{x}<br>Commits: %{y}<extra></extra>"), row=1, col=2)

    # [2,1] Barras horizontais — distribuicao por dominio detectado nos commits
    dc = df["domain"].value_counts()
    fig.add_trace(go.Bar(x=dc.values.tolist(), y=dc.index.tolist(), orientation="h",
        marker_color="#4B9EFF",
        hovertemplate="Dominio: %{y}<br>Commits: %{x}<extra></extra>"), row=2, col=1)

    # [2,2] Heatmap — estilo GitHub contributions
    # groupby + unstack cria pivot table: linhas=semanas, colunas=dias
    hp = df.groupby(["week","weekday"]).size().unstack(fill_value=0)
    # reindex garante todos os dias mesmo sem dados
    hp = hp.reindex(columns=WEEKDAY_ORDER, fill_value=0)
    # sorted() garante ordem cronologica
    hp = hp.loc[sorted(hp.index)]
    fig.add_trace(go.Heatmap(
        z=hp.values.T.tolist(),  # .T transpoe: dias no Y, semanas no X
        x=hp.index.tolist(), y=WEEKDAY_PT,
        colorscale=[[0.0,"#0F1117"],[0.01,"#1a2744"],[0.3,"#1d4ed8"],[0.6,"#0ea5e9"],[1.0,ACCENT]],
        showscale=True,
        colorbar=dict(title=dict(text="commits", font=dict(color=TEXT_COLOR)),
                      tickfont=dict(color=TEXT_COLOR), x=1.02),
        hovertemplate="Semana: %{x}<br>Dia: %{y}<br>Commits: %{z}<extra></extra>"), row=2, col=2)

    fig.update_layout(paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        height=700, showlegend=False,
        margin=dict(t=50, b=40, l=10, r=60))  # r=60 para acomodar colorbar
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)

    total_commits = len(df)
    total_labs    = (df["lab"] == "Sim").sum()  # boolean mask → contagem
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


# =============================================================================
# MONTAGEM DO HTML FINAL COM AS 3 ABAS
# Estrategia identica ao script 15 — CSS/JS puro para troca de abas
# Plotly carregado uma unica vez via CDN no <head>
# =============================================================================

def build_html(aba1, aba2, aba3):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard CCNP ENCORE 350-401 Modular</title>
  <!-- Plotly carregado uma unica vez — compartilhado por todas as abas -->
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
    /* Aba ativa: borda verde, fundo do body, margem negativa para grudar na linha */
    .tab-btn.active{{background:{BG_COLOR};color:{ACCENT};border:2px solid {ACCENT};
      border-bottom:2px solid {BG_COLOR};margin-bottom:-2px;}}
    /* Conteudo oculto por padrao — visivel apenas quando tem classe .active */
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
  <!-- HTML de cada aba injetado pelo Python via f-string -->
  <div id="resumo" class="tab-content active">{aba1}</div>
  <div id="progresso" class="tab-content">{aba2}</div>
  <div id="commits" class="tab-content">{aba3}</div>
  <script>
    function showTab(name){{
      // Remove .active de todos os conteudos e botoes
      document.querySelectorAll('.tab-content').forEach(el=>el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el=>el.classList.remove('active'));
      // Ativa o conteudo e botao correspondente ao nome clicado
      document.getElementById(name).classList.add('active');
      event.target.classList.add('active');
    }}
  </script>
</body>
</html>"""


# =============================================================================
# MAIN — Orquestrador
# Chama modulos na ordem correta e coordena a geracao do dashboard
# Comparacao com script 15:
#   Antes: main() chamava funcoes locais (extract_git_log, parse_lines, etc.)
#   Agora: main() chama funcoes importadas — logica identica, origem diferente
# =============================================================================

def main():
    args = parse_args()
    print(f"\n{'='*55}")
    print(f"  Dashboard Modular — CCNP ENCORE 350-401")
    print(f"  Repositorio : {args.repo}")
    print(f"  Blueprint   : {args.ccnp}")
    print(f"{'='*55}\n")

    validate_repo(args.repo)   # modulo extract.py — valida .git
    validate_ccnp(args.ccnp)   # orquestrador — valida pasta blueprint

    # Pipeline de dados via modulos importados
    lines   = extract_git_log(args.repo)   # modulo extract.py
    records = parse_lines(lines)            # modulo parser.py
    save_csv(records)                       # modulo parser.py
    df      = pd.read_csv(OUTPUT_CSV, parse_dates=["date"])

    domains = scan_blueprint(args.ccnp)    # modulo scanner.py

    print("Gerando dashboard...")
    aba1 = build_aba_resumo(domains, df)   # orquestrador
    aba2 = build_aba_progresso(domains)    # orquestrador
    aba3 = build_aba_commits(df)           # orquestrador

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(build_html(aba1, aba2, aba3))

    print(f"\n Concluido! Abra: {OUTPUT_HTML}\n")


# Garante que main() so executa quando chamado diretamente
# Nao executa quando importado como modulo por outro script
if __name__ == "__main__":
    main()
