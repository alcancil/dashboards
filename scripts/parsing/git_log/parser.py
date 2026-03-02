import csv
import os
from datetime import datetime


DELIMITER = "|"

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "processed", "git_log.csv")

ACTION_MAP = {
    "alterado":    "Alterado",
    "alteradoo":   "Alterado",
    "aletardo":    "Alterado",
    "aletrado":    "Alterado",
    "alterad":     "Alterado",
    "alterados":   "Alterado",
    "adicionado":  "Adicionado",
    "adicionando": "Adicionado",
    "adicionada":  "Adicionado",
    "adicioando":  "Adicionado",
    "adicioanado": "Adicionado",
    "adiconado":   "Adicionado",
    "ajustado":    "Ajustado",
    "ajuste":      "Ajustado",
    "acertado":    "Acertado",
    "arrumando":   "Acertado",
    "removido":    "Removido",
    "apagado":     "Removido",
    "realizado":   "Realizado",
    "separado":    "Separado",
    "dividido":    "Dividido",
    "criado":      "Criado",
    "corrigido":   "Corrigido",
    "atualizado":  "Atualizado",
    "update":      "Atualizado",
    "reanomeado":  "Renomeado",
    "teste":       "Teste",
    "vault":       "Outro",
    "initial":     "Outro",
}

DOMAIN_KEYWORDS = [
    ("architecture",      "Architecture"),
    ("virtualization",    "Virtualization"),
    ("virtualização",     "Virtualization"),
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
    ("network assurance", "Network Assurance"),
    ("assurance",         "Network Assurance"),
    ("netflow",           "Network Assurance"),
    ("snmp",              "Network Assurance"),
    ("syslog",            "Network Assurance"),
    ("security",          "Security"),
    ("segurança",         "Security"),
    ("acl",               "Security"),
    ("firewall",          "Security"),
    ("vpn",               "Security"),
    ("automation",        "Automation"),
    ("automação",         "Automation"),
    ("python",            "Automation"),
    ("netmiko",           "Automation"),
    ("paramiko",          "Automation"),
    ("ansible",           "Automation"),
    ("parsing",           "Automation"),
]


def extract_action(message):
    first_word = message.strip().split()[0].lower() if message.strip() else ""
    return ACTION_MAP.get(first_word, "Outro")


def extract_domain(message):
    msg_lower = message.lower()
    for keyword, domain in DOMAIN_KEYWORDS:
        if keyword in msg_lower:
            return domain
    return "Geral"


def extract_lab(message):
    msg_lower = message.lower()
    return "Sim" if "exemplo prático" in msg_lower or "exemplo pratico" in msg_lower else "Não"


def parse_lines(lines):
    records = []
    for line in lines:
        parts = line.split(DELIMITER, maxsplit=2)
        if len(parts) != 3:
            continue
        commit_hash, date_str, message = parts
        try:
            dt = datetime.fromisoformat(date_str.strip()[:19])
        except ValueError:
            continue
        records.append({
            "hash":    commit_hash.strip(),
            "date":    dt.strftime("%Y-%m-%d"),
            "week":    dt.strftime("%Y-W%W"),
            "weekday": dt.strftime("%A"),
            "message": message.strip(),
            "action":  extract_action(message),
            "domain":  extract_domain(message),
            "lab":     extract_lab(message),
        })
    print(f"[2/4] Parsing concluído: {len(records)} registros válidos")
    return records


def save_csv(records):
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    fieldnames = ["hash", "date", "week", "weekday", "message", "action", "domain", "lab"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"[3/4] CSV salvo: {OUTPUT_CSV}")