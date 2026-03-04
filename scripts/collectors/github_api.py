import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")

GITHUB_API  = "https://api.github.com"
TOKEN       = os.getenv("GITHUB_TOKEN")
REPO_DASH   = os.getenv("GITHUB_REPO_DASHBOARDS")
REPO_CISCO  = os.getenv("GITHUB_REPO_CISCO")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def _get(endpoint):
    url = f"{GITHUB_API}{endpoint}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def _get_paginated(endpoint):
    results = []
    page    = 1
    while True:
        url      = f"{GITHUB_API}{endpoint}?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        results.extend(data)
        page += 1
    return results


def collect_repo_info(repo):
    return _get(f"/repos/{repo}")


def collect_commits(repo):
    return _get_paginated(f"/repos/{repo}/commits")


def collect_commit_activity(repo):
    return _get(f"/repos/{repo}/stats/commit_activity")


def collect_contributors(repo):
    return _get(f"/repos/{repo}/stats/contributors")


def collect_contents(repo, path=""):
    return _get(f"/repos/{repo}/contents/{path}")


def save_raw(data, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[collector] Salvo: {filepath}")
    return filepath


def collect_all():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"\n{'='*55}")
    print(f"  Coleta GitHub API — {timestamp}")
    print(f"{'='*55}\n")

    print(f"[1/4] Coletando repositório: {REPO_DASH}")
    dash_info     = collect_repo_info(REPO_DASH)
    dash_commits  = collect_commits(REPO_DASH)
    dash_activity = collect_commit_activity(REPO_DASH)
    dash_contrib  = collect_contributors(REPO_DASH)

    print(f"[2/4] Coletando repositório: {REPO_CISCO}")
    cisco_info     = collect_repo_info(REPO_CISCO)
    cisco_commits  = collect_commits(REPO_CISCO)
    cisco_activity = collect_commit_activity(REPO_CISCO)
    cisco_contrib  = collect_contributors(REPO_CISCO)

    print(f"[3/4] Montando payload...")
    payload = {
        "collected_at": timestamp,
        "dashboards": {
            "info":     dash_info,
            "commits":  dash_commits,
            "activity": dash_activity,
            "contributors": dash_contrib,
        },
        "cisco": {
            "info":     cisco_info,
            "commits":  cisco_commits,
            "activity": cisco_activity,
            "contributors": cisco_contrib,
        },
    }

    print(f"[4/4] Salvando dados brutos...")
    filename = f"github_api_{timestamp}.json"
    save_raw(payload, filename)
    save_raw(payload, "github_api_latest.json")

    print(f"\n Coleta concluida!")
    print(f"   DASHBOARDS : {len(dash_commits)} commits")
    print(f"   CISCO      : {len(cisco_commits)} commits\n")

    return payload


if __name__ == "__main__":
    collect_all()
