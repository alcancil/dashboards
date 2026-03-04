# =============================================================================
# processor.py — Módulo de Processamento dos Dados da API do GitHub
# Responsabilidade única: transformar o JSON bruto coletado pelo github_api.py
# em DataFrames e CSVs estruturados prontos para visualização
#
# Faz parte do pacote: scripts/parsing/github/
# Importado por: src/avancado/17_github_metrics.py
#
# Funções exportadas:
#   process_all(raw_data=None) → (df_dash, df_cisco, df_all)
#
# Pipeline de dados:
#   data/raw/github_api_latest.json     ← entrada (gerado pelo github_api.py)
#         ↓
#   process_commits()                   ← transforma lista de commits em DataFrame
#   process_repo_info()                 ← extrai métricas gerais do repositório
#         ↓
#   data/processed/commits_dashboards.csv  ← saída: commits do DASHBOARDS
#   data/processed/commits_cisco.csv       ← saída: commits do CISCO
#   data/processed/commits_all.csv         ← saída: os dois combinados
#   data/processed/repo_info.json          ← saída: métricas gerais dos repos
#
# Observação sobre activity e contributors:
#   A API do GitHub retorna esses endpoints de forma assíncrona — na primeira
#   chamada retorna 202 (processando) e devolve {} vazio. Por isso usamos
#   apenas os commits, que são síncronos e contêm todos os dados necessários.
# =============================================================================

import os
import json
import pandas as pd
from datetime import datetime


# Caminhos calculados a partir da posição deste arquivo
# scripts/parsing/github/ → (1) parsing/ → (2) scripts/ → (3) DASHBOARDS/ (raiz)
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW_DIR       = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

# Arquivo fixo que o collector sempre atualiza com a coleta mais recente
LATEST_JSON = os.path.join(RAW_DIR, "github_api_latest.json")

# Tipos válidos no padrão Conventional Commits
# Usados para classificar commits do repositório DASHBOARDS
# Commits do CISCO não seguem esse padrão — serão classificados como "outro"
CONVENTIONAL_TYPES = [
    "feat", "fix", "docs", "style", "refactor",
    "test", "chore", "perf", "ci", "build"
]


def load_raw(filepath=None):
    # Se nenhum arquivo for especificado, usa o _latest (coleta mais recente)
    # Permite passar um arquivo específico para reprocessar coletas antigas
    path = filepath or LATEST_JSON
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_commit_type(message):
    # Detecta o tipo do commit pela primeira palavra da mensagem
    # Conventional Commits: "feat(avancado): adiciona..." → tipo = "feat"
    # Commits sem padrão: "Alterado o Readme.md" → tipo = "outro"
    # .lower() normaliza para evitar problemas com maiúsculas
    msg = message.strip().lower()
    for t in CONVENTIONAL_TYPES:
        if msg.startswith(t):
            return t
    return "outro"


def _parse_commit_scope(message):
    # Extrai o escopo entre parênteses: "feat(avancado): ..." → "avancado"
    # maxsplit não é necessário aqui pois split("(")[1] já pega o primeiro grupo
    # try/except protege contra mensagens mal formatadas que tenham ( mas não )
    msg = message.strip()
    if "(" in msg and ")" in msg:
        try:
            return msg.split("(")[1].split(")")[0].lower()
        except IndexError:
            pass
    return "geral"  # fallback para commits sem escopo definido


def process_commits(commits, repo_name):
    records = []
    for c in commits:
        author  = c["commit"]["author"]

        # pd.to_datetime com utc=True converte o timestamp ISO 8601 da API
        # tz_convert(None) remove o timezone após conversão — facilita comparações
        date    = pd.to_datetime(author["date"], utc=True).tz_convert(None)

        # Pega apenas a primeira linha da mensagem — ignora corpo e rodapé do commit
        message = c["commit"]["message"].split("\n")[0].strip()

        records.append({
            "repo":    repo_name,           # "dashboards" ou "cisco"
            "sha":     c["sha"][:7],        # hash curto de 7 caracteres (padrão git)
            "date":    date.date(),         # apenas a data, sem hora
            "week":    date.strftime("%Y-W%W"),  # ex: "2026-W09" — para agrupamento semanal
            "month":   date.strftime("%Y-%m"),   # ex: "2026-03" — para agrupamento mensal
            "weekday": date.strftime("%A"),      # ex: "Monday" — para o heatmap
            "message": message,
            "type":    _parse_commit_type(message),   # feat, fix, docs, outro...
            "scope":   _parse_commit_scope(message),  # avancado, readme, geral...
        })

    # Retorna DataFrame — estrutura tabular do pandas, ideal para análise e plot
    return pd.DataFrame(records)


def process_repo_info(info, repo_name):
    # Extrai apenas os campos relevantes do JSON de info do repositório
    # O JSON bruto tem ~100 campos — filtramos os que realmente usamos
    return {
        "repo":           repo_name,
        "full_name":      info.get("full_name"),
        "stars":          info.get("stargazers_count", 0),
        "forks":          info.get("forks_count", 0),
        "size_kb":        info.get("size", 0),
        "created_at":     info.get("created_at", ""),
        "pushed_at":      info.get("pushed_at", ""),
        "open_issues":    info.get("open_issues_count", 0),
        "default_branch": info.get("default_branch", "main"),
    }


def save_csv(df, filename):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    filepath = os.path.join(PROCESSED_DIR, filename)
    # index=False evita salvar o índice numérico do DataFrame como coluna extra
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"[processor] Salvo: {filepath} ({len(df)} registros)")
    return filepath


def save_json(data, filename):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    filepath = os.path.join(PROCESSED_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[processor] Salvo: {filepath}")
    return filepath


def process_all(raw_data=None):
    # raw_data opcional — se não passado, lê do arquivo _latest
    # Permite que o orquestrador (script 17) passe os dados já carregados
    # evitando dupla leitura do arquivo
    data = raw_data or load_raw()

    print(f"\n{'='*55}")
    print(f"  Processamento GitHub API")
    print(f"  Coletado em: {data.get('collected_at', 'desconhecido')}")
    print(f"{'='*55}\n")

    print("[1/4] Processando commits DASHBOARDS...")
    df_dash = process_commits(data["dashboards"]["commits"], "dashboards")

    print("[2/4] Processando commits CISCO...")
    df_cisco = process_commits(data["cisco"]["commits"], "cisco")

    print("[3/4] Combinando datasets...")
    # pd.concat combina os dois DataFrames verticalmente (axis=0 por padrão)
    # ignore_index=True reinicia o índice — evita duplicatas de índice
    # sort_values por data decrescente — commit mais recente primeiro
    df_all = pd.concat([df_dash, df_cisco], ignore_index=True)
    df_all = df_all.sort_values("date", ascending=False).reset_index(drop=True)

    print("[4/4] Salvando CSVs e métricas...")
    save_csv(df_dash,  "commits_dashboards.csv")
    save_csv(df_cisco, "commits_cisco.csv")
    save_csv(df_all,   "commits_all.csv")

    # Salva info dos dois repositórios em JSON — usado pelos cards do dashboard
    info_dash  = process_repo_info(data["dashboards"]["info"], "dashboards")
    info_cisco = process_repo_info(data["cisco"]["info"],      "cisco")
    save_json({"dashboards": info_dash, "cisco": info_cisco}, "repo_info.json")

    print(f"\n Processamento concluido!")
    print(f"   DASHBOARDS : {len(df_dash)} commits | {df_dash['week'].nunique()} semanas")
    print(f"   CISCO      : {len(df_cisco)} commits | {df_cisco['week'].nunique()} semanas\n")

    # Retorna os três DataFrames para uso direto pelo orquestrador
    return df_dash, df_cisco, df_all


# Permite rodar o módulo diretamente para testar o processamento
# python scripts/parsing/github/processor.py
if __name__ == "__main__":
    process_all()
