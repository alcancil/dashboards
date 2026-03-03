import os


DOMAIN_ORDER = [
    "01 - Architecture",
    "02 - Virtualization",
    "03 - Infrastructure",
    "04 - Network Assurance",
    "05 - Security",
    "06 - Automation",
]

DOMAIN_COLORS = {
    "01 - Architecture":      "#00C896",
    "02 - Virtualization":    "#4B9EFF",
    "03 - Infrastructure":    "#FB923C",
    "04 - Network Assurance": "#A78BFA",
    "05 - Security":          "#FF4B4B",
    "06 - Automation":        "#FACC15",
}

SKIP_FOLDERS = {"Arquivos", "Imagens", "Simulado"}


def scan_blueprint(ccnp_path):
    domains = {}

    for domain_name in DOMAIN_ORDER:
        domain_path = os.path.join(ccnp_path, domain_name)

        if not os.path.isdir(domain_path):
            domains[domain_name] = {"topics": {}, "total_subtopics": 0, "total_labs": 0}
            continue

        topics = {}
        for topic in sorted(os.listdir(domain_path)):
            topic_path = os.path.join(domain_path, topic)
            if not os.path.isdir(topic_path):
                continue

            subtopics = []
            labs      = []

            for sub in sorted(os.listdir(topic_path)):
                sub_path = os.path.join(topic_path, sub)
                if not os.path.isdir(sub_path):
                    continue
                if sub in SKIP_FOLDERS:
                    continue
                subtopics.append(sub)
                if "exemplo pr" in sub.lower() or "exemplo pratico" in sub.lower():
                    labs.append(sub)

            topics[topic] = {"subtopics": subtopics, "labs": labs}

        total_subtopics = sum(len(v["subtopics"]) for v in topics.values())
        total_labs      = sum(len(v["labs"])      for v in topics.values())

        domains[domain_name] = {
            "topics":          topics,
            "total_subtopics": total_subtopics,
            "total_labs":      total_labs,
        }

    print(f"[blueprint] Escaneado: {len(domains)} domínios")
    return domains