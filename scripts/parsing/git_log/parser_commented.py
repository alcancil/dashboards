# =============================================================================
# parser.py — Módulo de Parsing e Exportação CSV
# Responsabilidade: transformar linhas brutas do git log em registros estruturados
# e exportar como CSV
#
# Faz parte do pacote: scripts/parsing/git_log/
# Importado por: src/avancado/14_git_log_modular.py
#
# Funções exportadas:
#   parse_lines(lines)  → converte lista de linhas brutas em lista de dicionários
#   save_csv(records)   → salva os dicionários em data/processed/git_log.csv
#
# Filosofia: sem regex — apenas split(), strip(), lower() e operador 'in'
# =============================================================================

import csv          # Escrita de arquivos CSV com DictWriter
import os           # Manipulação de caminhos portáveis
from datetime import datetime  # Conversão e formatação de datas


DELIMITER = "|"

# BASE_DIR: sobe 4 níveis a partir deste arquivo para chegar à raiz do projeto
# Este arquivo está em: scripts/parsing/git_log/parser.py
#   dirname 1x → scripts/parsing/git_log/
#   dirname 2x → scripts/parsing/
#   dirname 3x → scripts/
#   dirname 4x → DASHBOARDS/ (raiz)
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "processed", "git_log.csv")

# -----------------------------------------------------------------------------
# DICIONÁRIO DE NORMALIZAÇÃO DE VERBOS (ACTION_MAP)
#
# Problema: o repositório CCNP ainda não usa Conventional Commits,
# então as mensagens têm variações e typos nos verbos de ação.
#
# Solução sem regex: dicionário de lookup simples.
# Pegamos a primeira palavra da mensagem, convertemos para lowercase,
# e buscamos no dicionário para obter a forma canônica padronizada.
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
# Lista de tuplas (palavra-chave, domínio).
# Percorrida em ordem — primeira correspondência vence.
# Palavras mais específicas vêm antes das mais genéricas.
# Operador 'in' faz busca de substring após converter mensagem para lowercase.
# -----------------------------------------------------------------------------
DOMAIN_KEYWORDS = [
    # Domínio: Architecture
    ("architecture",      "Architecture"),

    # Domínio: Virtualization
    ("virtualization",    "Virtualization"),
    ("virtualização",     "Virtualization"),

    # Domínio: Infrastructure
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


def extract_action(message):
    # split() divide a mensagem em palavras pelo espaço
    # [0] pega a primeira palavra (o verbo de ação)
    # .lower() converte para minúsculo para comparação uniforme
    # .get(first_word, "Outro") busca no dicionário; retorna "Outro" se não encontrar
    first_word = message.strip().split()[0].lower() if message.strip() else ""
    return ACTION_MAP.get(first_word, "Outro")


def extract_domain(message):
    # Converte a mensagem inteira para lowercase uma única vez
    # O operador 'in' funciona como substring search — sem regex
    # A primeira correspondência encontrada é retornada (ordem da lista importa)
    msg_lower = message.lower()
    for keyword, domain in DOMAIN_KEYWORDS:
        if keyword in msg_lower:
            return domain
    return "Geral"  # nenhuma palavra-chave encontrada


def extract_lab(message):
    # Verifica se a mensagem menciona "Exemplo Prático" ou "Exemplo Pratico"
    # (com e sem acento) — padrão usado para nomear pastas de laboratório no CCNP
    # Retorna string "Sim"/"Não" para facilitar leitura no CSV
    msg_lower = message.lower()
    return "Sim" if "exemplo prático" in msg_lower or "exemplo pratico" in msg_lower else "Não"


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


def save_csv(records):
    # exist_ok=True evita erro se o diretório já existir
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    # fieldnames define a ordem das colunas no arquivo CSV
    fieldnames = ["hash", "date", "week", "weekday", "message", "action", "domain", "lab"]

    # newline="" é recomendado no Windows para evitar linhas em branco extras
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()       # escreve a linha de cabeçalho com os nomes das colunas
        writer.writerows(records)  # escreve todos os registros de uma vez

    print(f"[3/4] CSV salvo: {OUTPUT_CSV}")