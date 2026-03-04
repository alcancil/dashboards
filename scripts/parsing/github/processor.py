import os
import json
import pandas as pd
from datetime import datetime

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW_DIR       = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

LATEST_JSON = os.path.join(RAW_DIR, "github_api_latest.json")

CONVENTIONAL_TYPES = [
    "feat", "fix", "docs", "style", "refactor",
    "test", "chore", "perf", "ci", "build"
]


def load_raw(filepath=None):
    path = filepath or LATEST_JSON
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_commit_type(message):
    msg = message.strip().lower()
    for t in CONVENTIONAL_TYPES:
        if msg.startswith(t):
            return t
    return "outro"


def _parse_commit_scope(message):
    msg = message.strip()
    if "(" in msg and ")" in msg:
        try:
            return msg.split("(")[1].split(")")[0].lower()
        except IndexError:
            pass
    return "geral"


def process_commits(commits, repo_name):
    records = []
    for c in commits:
        author  = c["commit"]["author"]
        date    = pd.to_datetime(author["date"], utc=True).tz_convert(None)
        message = c["commit"]["message"].split("\n")[0].strip()

        records.append({
            "repo":       repo_name,
            "sha":        c["sha"][:7],
            "date":       date.date(),
            "week":       date.strftime("%Y-W%W"),
            "month":      date.strftime("%Y-%m"),
            "weekday":    date.strftime("%A"),
            "message":    message,
            "type":       _parse_commit_type(message),
            "scope":      _parse_commit_scope(message),
        })
    return pd.DataFrame(records)


def process_repo_info(info, repo_name):
    return {
        "repo":          repo_name,
        "full_name":     info.get("full_name"),
        "stars":         info.get("stargazers_count", 0),
        "forks":         info.get("forks_count", 0),
        "size_kb":       info.get("size", 0),
        "created_at":    info.get("created_at", ""),
        "pushed_at":     info.get("pushed_at", ""),
        "open_issues":   info.get("open_issues_count", 0),
        "default_branch":info.get("default_branch", "main"),
    }


def save_csv(df, filename):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    filepath = os.path.join(PROCESSED_DIR, filename)
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
    df_all = pd.concat([df_dash, df_cisco], ignore_index=True)
    df_all = df_all.sort_values("date", ascending=False).reset_index(drop=True)

    print("[4/4] Salvando CSVs e métricas...")
    save_csv(df_dash,  "commits_dashboards.csv")
    save_csv(df_cisco, "commits_cisco.csv")
    save_csv(df_all,   "commits_all.csv")

    info_dash  = process_repo_info(data["dashboards"]["info"], "dashboards")
    info_cisco = process_repo_info(data["cisco"]["info"],      "cisco")
    save_json({"dashboards": info_dash, "cisco": info_cisco}, "repo_info.json")

    print(f"\n Processamento concluido!")
    print(f"   DASHBOARDS : {len(df_dash)} commits | {df_dash['week'].nunique()} semanas")
    print(f"   CISCO      : {len(df_cisco)} commits | {df_cisco['week'].nunique()} semanas\n")

    return df_dash, df_cisco, df_all


if __name__ == "__main__":
    process_all()
