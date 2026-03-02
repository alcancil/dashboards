import subprocess
import os


DELIMITER = "|"

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
OUTPUT_RAW = os.path.join(BASE_DIR, "data", "raw", "raw_git_log.txt")


def validate_repo(repo_path):
    if not os.path.isdir(repo_path):
        raise FileNotFoundError(f"Repositório não encontrado: {repo_path}")
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        raise ValueError(f"O caminho existe mas não é um repositório Git: {repo_path}")


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