# =============================================================================
# extract.py — Módulo de Extração
# Responsabilidade única: executar o git log e salvar o output bruto
#
# Faz parte do pacote: scripts/parsing/git_log/
# Importado por: src/avancado/14_git_log_modular.py
#
# Funções exportadas:
#   validate_repo(repo_path) → valida se o caminho é um repositório Git válido
#   extract_git_log(repo_path) → executa git log e retorna lista de linhas brutas
# =============================================================================

import subprocess  # Executa comandos do sistema operacional (git log)
import os          # Manipulação de caminhos portáveis entre Windows e Linux


# Delimitador usado no git log --pretty=format
# Escolhemos "|" porque raramente aparece em mensagens de commit
DELIMITER = "|"

# BASE_DIR: sobe 5 níveis a partir deste arquivo para chegar à raiz do projeto
# Este arquivo está em: scripts/parsing/git_log/extract.py
#   scripts/parsing/git_log/ → (1) scripts/parsing/ → (2) scripts/
#   → (3) raiz do projeto (DASHBOARDS/)
# Contamos a partir do abspath do __file__:
#   dirname 1x → scripts/parsing/git_log/
#   dirname 2x → scripts/parsing/
#   dirname 3x → scripts/
#   dirname 4x → DASHBOARDS/ (raiz)
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUTPUT_RAW = os.path.join(BASE_DIR, "data", "raw", "raw_git_log.txt")


def validate_repo(repo_path):
    # Fail fast: verifica tudo antes de executar qualquer etapa do pipeline
    # Evita erros confusos no meio da execução

    # os.path.isdir verifica se o caminho existe e é um diretório
    if not os.path.isdir(repo_path):
        raise FileNotFoundError(f"Repositório não encontrado: {repo_path}")

    # Todo repositório Git possui uma pasta oculta .git na raiz
    # Se ela não existir, o caminho informado não é um repositório Git válido
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        raise ValueError(f"O caminho existe mas não é um repositório Git: {repo_path}")


def extract_git_log(repo_path):
    # exist_ok=True evita erro se o diretório já existir
    os.makedirs(os.path.dirname(OUTPUT_RAW), exist_ok=True)

    # subprocess.run executa o git log como se fosse no terminal
    # Lista de strings evita problemas com espaços nos caminhos
    # cwd=repo_path    → muda o diretório de trabalho para o repositório informado
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

    # returncode != 0 indica que o git encontrou um erro na execução
    if result.returncode != 0:
        raise RuntimeError(f"Erro ao executar git log: {result.stderr}")

    # Salva o output bruto em data/raw/ — fonte da verdade, nunca editar manualmente
    # Este arquivo está no .gitignore pois contém paths locais da máquina
    with open(OUTPUT_RAW, "w", encoding="utf-8") as f:
        f.write(result.stdout)

    # splitlines() divide o output em lista de linhas
    # O filtro 'if l.strip()' remove linhas vazias antes de contar
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    print(f"[1/4] Git log extraído: {len(lines)} commits → {OUTPUT_RAW}")
    return lines