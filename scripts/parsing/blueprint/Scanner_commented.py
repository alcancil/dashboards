# =============================================================================
# scanner_commented.py — Módulo de Leitura da Estrutura do Blueprint CCNP ENCORE
# Responsabilidade única: escanear a estrutura de pastas do repositório CISCO
# e retornar um dicionário estruturado com domínios, tópicos, subtópicos e labs
#
# Faz parte do pacote: scripts/parsing/blueprint/
# Importado por: src/avancado/16_dashboard_completo_modular.py
#
# Funções exportadas:
#   scan_blueprint(ccnp_path) → dicionário com estrutura completa do blueprint
#
# Por que está em scripts/parsing/ e não em scripts/blueprint/?
#   scan_blueprint() é uma forma de parsing — lê uma estrutura (pastas) e
#   transforma em dados estruturados (dicionário). Mesma responsabilidade
#   semântica de extract.py (lê git log) e parser.py (transforma em registros),
#   porém para outra fonte de dados: o sistema de arquivos.
#
# Estrutura esperada no disco:
#   ccnp_path/
#   ├── 01 - Architecture/           ← domínio
#   │   ├── 01 - QoS/                ← tópico
#   │   │   ├── 01 - Limite de Banda/  ← subtópico (contabilizado)
#   │   │   ├── 10 - Exemplo Prático/  ← subtópico + lab (contabilizado)
#   │   │   └── Arquivos/              ← ignorado (SKIP_FOLDERS)
#   └── 02 - Virtualization/
# =============================================================================

import os  # Listagem de diretórios e manipulação de caminhos portáveis


# Ordem fixa dos 6 domínios do Blueprint ENCORE 350-401
# Usamos lista (não set) para garantir sempre a mesma sequência nos gráficos,
# independente da ordem em que o OS retorna os arquivos
DOMAIN_ORDER = [
    "01 - Architecture",
    "02 - Virtualization",
    "03 - Infrastructure",
    "04 - Network Assurance",
    "05 - Security",
    "06 - Automation",
]

# Cor de destaque para cada domínio — exportada junto com scan_blueprint()
# O orquestrador importa DOMAIN_COLORS daqui para usar nos gráficos
# Centralizar aqui evita duplicação de dados entre módulo e orquestrador
DOMAIN_COLORS = {
    "01 - Architecture":      "#00C896",  # verde
    "02 - Virtualization":    "#4B9EFF",  # azul
    "03 - Infrastructure":    "#FB923C",  # laranja
    "04 - Network Assurance": "#A78BFA",  # roxo
    "05 - Security":          "#FF4B4B",  # vermelho
    "06 - Automation":        "#FACC15",  # amarelo
}

# Set de pastas de suporte presentes dentro de cada tópico mas que NÃO
# representam subtópicos de estudo — devem ser ignoradas na contagem
# Set é mais eficiente que lista para lookup com operador 'in'
SKIP_FOLDERS = {"Arquivos", "Imagens", "Simulado"}


def scan_blueprint(ccnp_path):
    domains = {}  # dicionário final indexado pelo nome do domínio

    for domain_name in DOMAIN_ORDER:
        # os.path.join monta o caminho de forma portável (Windows e Linux)
        domain_path = os.path.join(ccnp_path, domain_name)

        # Se o domínio ainda não existe no disco (ex: 04 - Network Assurance),
        # registra como vazio para garantir que apareça nos gráficos com valor zero
        if not os.path.isdir(domain_path):
            domains[domain_name] = {"topics": {}, "total_subtopics": 0, "total_labs": 0}
            continue

        topics = {}

        # sorted() garante ordem numérica dos tópicos (01, 02, 03...)
        # independente de como o OS retorna os arquivos (pode variar entre Windows/Linux)
        for topic in sorted(os.listdir(domain_path)):
            topic_path = os.path.join(domain_path, topic)

            # os.path.isdir() filtra arquivos soltos — só processa pastas de tópico
            if not os.path.isdir(topic_path):
                continue

            subtopics = []
            labs      = []

            for sub in sorted(os.listdir(topic_path)):
                sub_path = os.path.join(topic_path, sub)

                # Filtra arquivos soltos dentro do tópico
                if not os.path.isdir(sub_path):
                    continue

                # Operador 'in' com set é O(1) — mais eficiente que lista
                # Ignora pastas de suporte que não são subtópicos de estudo
                if sub in SKIP_FOLDERS:
                    continue

                subtopics.append(sub)

                # Detecta labs pela presença de "Exemplo Pr" no nome da pasta
                # .lower() normaliza para evitar problemas com maiúsculas/minúsculas
                # "exemplo pr" cobre variações: "Prático", "Pratico", "Prßtico" (encoding Windows)
                if "exemplo pr" in sub.lower() or "exemplo pratico" in sub.lower():
                    labs.append(sub)

            topics[topic] = {"subtopics": subtopics, "labs": labs}

        # Generator expression dentro de sum() — itera sem criar lista intermediária
        # Soma o total de subtópicos de todos os tópicos do domínio
        total_subtopics = sum(len(v["subtopics"]) for v in topics.values())
        total_labs      = sum(len(v["labs"])      for v in topics.values())

        domains[domain_name] = {
            "topics":          topics,          # estrutura completa: tópico → subtópicos + labs
            "total_subtopics": total_subtopics, # total para uso direto nos gráficos
            "total_labs":      total_labs,      # total de labs para uso nos cards e tabela
        }

    print(f"[blueprint] Escaneado: {len(domains)} domínios")
    return domains