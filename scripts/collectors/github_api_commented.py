# =============================================================================
# github_api.py — Módulo de Coleta via API do GitHub
# Responsabilidade única: fazer chamadas à API do GitHub e salvar os dados
# brutos em data/raw/ como JSON — sem transformação, sem processamento
#
# Faz parte do pacote: scripts/collectors/
# Importado por: src/avancado/17_github_metrics.py
#
# Funções exportadas:
#   collect_all() → coleta os dois repositórios e salva em data/raw/
#
# Nível de segurança atual: Nível 1 — .env + .gitignore
#   O token é lido do arquivo .env via python-dotenv
#   PROBLEMA: token em texto claro no disco local
#   PRÓXIMO PASSO (Nível 3): GitHub Actions Secrets — token nunca toca o disco
#
# Endpoints utilizados:
#   GET /repos/{owner}/{repo}                  → info geral do repositório
#   GET /repos/{owner}/{repo}/commits          → lista de commits (paginado)
#   GET /repos/{owner}/{repo}/stats/commit_activity → commits por semana (52 semanas)
#   GET /repos/{owner}/{repo}/stats/contributors    → stats por contribuidor
#
# Estratégia de persistência:
#   - Salva arquivo com timestamp: github_api_20260303_142000.json (histórico)
#   - Salva arquivo fixo: github_api_latest.json (sempre o mais recente)
#   - Cada execução ACUMULA histórico — não sobrescreve arquivos anteriores
# =============================================================================

import os                          # Caminhos portáveis e variáveis de ambiente
import json                        # Serialização dos dados para arquivo
import requests                    # Requisições HTTP para a API do GitHub
from datetime import datetime      # Timestamp da coleta
from dotenv import load_dotenv     # Lê variáveis do arquivo .env


# load_dotenv() lê o arquivo .env na raiz do projeto e injeta as variáveis
# no ambiente do processo — depois acessamos com os.getenv()
load_dotenv()

# BASE_DIR: sobe 3 níveis a partir de scripts/collectors/ para chegar à raiz
#   scripts/collectors/ → (1) scripts/ → (2) DASHBOARDS/ (raiz)
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")

# URL base da API REST do GitHub v3
GITHUB_API = "https://api.github.com"

# Lê as variáveis do .env — nunca hardcoded no código
TOKEN      = os.getenv("GITHUB_TOKEN")               # ex: ghp_xxx
REPO_DASH  = os.getenv("GITHUB_REPO_DASHBOARDS")     # ex: alcancil/dashboards
REPO_CISCO = os.getenv("GITHUB_REPO_CISCO")          # ex: alcancil/ccnp-enterprise-lab

# Headers padrão para todas as requisições
# Authorization: token é o formato clássico do GitHub (Personal Access Token)
# Accept: vnd.github.v3+json garante que usamos a versão 3 da API
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def _get(endpoint):
    # Função interna — prefixo _ indica que não é parte da API pública do módulo
    # raise_for_status() lança exceção se o status HTTP for 4xx ou 5xx
    # Isso faz o script falhar rápido com mensagem clara em vez de retornar dados vazios
    url = f"{GITHUB_API}{endpoint}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def _get_paginated(endpoint):
    # A API do GitHub retorna no máximo 100 itens por página
    # Para repositórios com muitos commits precisamos paginar
    # Loop continua até receber uma página vazia — sinal de fim dos dados
    results = []
    page    = 1
    while True:
        url      = f"{GITHUB_API}{endpoint}?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if not data:
            break          # página vazia = chegou ao fim
        results.extend(data)
        page += 1
    return results


def collect_repo_info(repo):
    # Retorna metadados gerais: nome, descrição, estrelas, forks,
    # linguagem principal, data de criação, último push, tamanho
    return _get(f"/repos/{repo}")


def collect_commits(repo):
    # Lista todos os commits do repositório com paginação automática
    # Cada commit contém: sha, autor, data, mensagem
    # Usamos _get_paginated pois repositórios com muitos commits ultrapassam 100
    return _get_paginated(f"/repos/{repo}/commits")


def collect_commit_activity(repo):
    # Retorna array com 52 semanas de atividade
    # Cada item: { week: timestamp_unix, days: [dom,seg,...,sab], total: int }
    # ATENÇÃO: endpoint pode retornar 202 (processando) na primeira chamada
    # Se retornar lista vazia, aguarde alguns segundos e tente novamente
    return _get(f"/repos/{repo}/stats/commit_activity")


def collect_contributors(repo):
    # Retorna estatísticas por contribuidor
    # Cada item: { author: {...}, total: int, weeks: [...] }
    # weeks contém: { w: timestamp, a: adições, d: deleções, c: commits }
    return _get(f"/repos/{repo}/stats/contributors")


def collect_contents(repo, path=""):
    # Lista arquivos e pastas de um caminho dentro do repositório
    # path="" lista a raiz; path="src/avancado" lista aquela pasta
    # Útil para verificar estrutura de pastas sem clonar o repositório
    return _get(f"/repos/{repo}/contents/{path}")


def save_raw(data, filename):
    # exist_ok=True evita erro se o diretório já existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    # ensure_ascii=False preserva caracteres especiais (ã, ç, etc.)
    # indent=2 formata o JSON de forma legível — facilita debug manual
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[collector] Salvo: {filepath}")
    return filepath


def collect_all():
    # Função principal — orquestra toda a coleta
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"\n{'='*55}")
    print(f"  Coleta GitHub API — {timestamp}")
    print(f"{'='*55}\n")

    # Coleta repositório DASHBOARDS
    # 4 endpoints por repositório: info, commits, activity, contributors
    print(f"[1/4] Coletando repositório: {REPO_DASH}")
    dash_info     = collect_repo_info(REPO_DASH)
    dash_commits  = collect_commits(REPO_DASH)
    dash_activity = collect_commit_activity(REPO_DASH)
    dash_contrib  = collect_contributors(REPO_DASH)

    # Coleta repositório CISCO — mesmos endpoints, outro repositório
    print(f"[2/4] Coletando repositório: {REPO_CISCO}")
    cisco_info     = collect_repo_info(REPO_CISCO)
    cisco_commits  = collect_commits(REPO_CISCO)
    cisco_activity = collect_commit_activity(REPO_CISCO)
    cisco_contrib  = collect_contributors(REPO_CISCO)

    print(f"[3/4] Montando payload...")
    # Payload único com os dados dos dois repositórios + timestamp da coleta
    # collected_at permite saber exatamente quando os dados foram coletados
    # Isso é fundamental para a análise histórica — sem timestamp, não há série temporal
    payload = {
        "collected_at": timestamp,
        "dashboards": {
            "info":         dash_info,
            "commits":      dash_commits,
            "activity":     dash_activity,
            "contributors": dash_contrib,
        },
        "cisco": {
            "info":         cisco_info,
            "commits":      cisco_commits,
            "activity":     cisco_activity,
            "contributors": cisco_contrib,
        },
    }

    print(f"[4/4] Salvando dados brutos...")

    # Salva dois arquivos:
    # 1. Com timestamp — acumula histórico (nunca sobrescreve)
    # 2. _latest — sempre o arquivo mais recente (fácil de apontar no processador)
    filename = f"github_api_{timestamp}.json"
    save_raw(payload, filename)
    save_raw(payload, "github_api_latest.json")

    print(f"\n Coleta concluida!")
    print(f"   DASHBOARDS : {len(dash_commits)} commits")
    print(f"   CISCO      : {len(cisco_commits)} commits\n")

    return payload


# Permite rodar o módulo diretamente para testar a coleta
# python scripts/collectors/github_api.py
if __name__ == "__main__":
    collect_all()
