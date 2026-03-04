# CCNP Lab Dashboard 📊

Dashboard interativo para visualização de progresso nos estudos CCNP Enterprise.

---

## 📋 Índice

- [Objetivos do Projeto](#-objetivos-do-projeto)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Gráficos Disponíveis](#-gráficos-disponíveis)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Visualização Online](#-visualização-online)
- [Arquivos de Configuração](#arquivos-de-configuração)
- [Pastas Principais](#pastas-principais)
- [Workflow Git Profissional](#-workflow-git-profissional)
- [Roadmap](#️-roadmap)
- [Contribuindo](#-contribuindo)
- [Changelog](#-changelog)
- [Licença](#-licença)
- [Contato](#-contato)
- [Repositório Principal](#-repositório-principal)

---

## 🎯 Objetivos do Projeto  

Este repositório documenta minha jornada de aprendizado prático, combinando três objetivos:

- Aprender Plotly - Do básico ao avançado, criando visualizações interativas
- Dashboard Profissional - Painel para acompanhar progresso dos 80+ labs CCNP
- Git Workflow - Praticar versionamento profissional com commits semânticos
- Integração - Conectar com scripts de automação (Netmiko/Paramiko)

---

## 📁 Estrutura do Projeto  

```bash
dashboards/
│
├── src/                                              # Código-fonte organizado por nível
│   │
│   ├── basico/                                       # 📘 Gráficos básicos e fundamentos
│   │   ├── 01_line_chart.py                          # Gráfico de linha (limpo)
│   │   ├── 01_line_chart_commented.py                # Gráfico de linha (comentado)
│   │   ├── 02_bar_chart.py                           # Gráfico de barras (limpo)
│   │   ├── 02_bar_chart_commented.py                 # Gráfico de barras (comentado)
│   │   ├── 03_pie_chart.py                           # Gráfico de pizza (limpo)
│   │   ├── 03_pie_chart_commented.py                 # Gráfico de pizza (comentado)
│   │   ├── 04_dashboard_mvp.py                       # Dashboard MVP (limpo)
│   │   └── 04_dashboard_mvp_commented.py             # Dashboard MVP (comentado)
│   │
│   ├── intermediario/                                # 📗 Gráficos intermediários
│   │   ├── 05_scatter_latency.py                     # Scatter: latência vs perda
│   │   ├── 05_scatter_latency_commented.py           # Scatter (comentado)
│   │   ├── 06_heatmap_devices.py                     # Heatmap: utilização 24h
│   │   ├── 06_heatmap_devices_commented.py           # Heatmap (comentado)
│   │   ├── 07_gauge_bandwidth.py                     # Gauge - Monitoramento de Banda (limpo)
│   │   ├── 07_gauge_bandwidth_commented.py           # Gauge - Monitoramento de Banda (comentado)
│   │   ├── 08_timeline_maintenance.py                # Timeline - Gráfico de Gantt (limpo)
│   │   ├── 08_timeline_maintenance_commented.py      # Timeline - Gráfico de Gantt (comentado)
│   │   ├── 09_dashboard_intermediario.py             # Dashboard Intermediário (limpo)
│   │   ├── 09_dashboard_intermediario_commented.py   # Dashboard Intermediário (comentado)
│   │   ├── 10_interactive_filters.py                 # Dashboard Interativo (limpo)
│   │   └── 10_interactive_filters_commented.py       # Dashboard Interativo (comentado)
│   │
│   └── avancado/                                     # 📕 Dashboards avançados
│       ├── 11_read_progress.py                       # Leitura de progresso CCNP (limpo)
│       ├── 11_read_progress_commented.py             # Leitura de progresso CCNP (comentado)
│       ├── 12_dashboard_progress.py                  # Dashboard progresso por acumulação (limpo)
│       ├── 12_dashboard_progress_commented.py        # Dashboard progresso por acumulação (comentado)
│       ├── 13_git_log_pipeline.py                    # Pipeline git log → CSV → Dashboard (limpo)
│       ├── 13_git_log_pipeline_commented.py          # Pipeline git log (comentado)
│       ├── 14_git_log_modular.py                     # Pipeline modularizado (limpo)
│       ├── 14_git_log_modular_commented.py           # Pipeline modularizado (comentado)
│       ├── 15_dashboard_completo.py                  # Dashboard 3 abas monolítico (limpo)
│       ├── 15_dashboard_completo_commented.py        # Dashboard 3 abas monolítico (comentado)
│       ├── 16_dashboard_completo_modular.py          # Dashboard 3 abas modular (limpo)
│       └── 16_dashboard_completo_modular_commented.py# Dashboard 3 abas modular (comentado)
│
├── scripts/                                          # 🔧 Scripts de pipeline de dados
│   └── parsing/                                      # Transformação de dados brutos
│       ├── git_log/                                  # Módulos de extração e parsing do git log
│       │   ├── __init__.py                           # Inicializa o pacote git_log
│       │   ├── extract.py                            # Extração do git log via subprocess (limpo)
│       │   ├── extract_commented.py                  # Extração (comentado)
│       │   ├── parser.py                             # Parsing e geração do CSV (limpo)
│       │   └── parser_commented.py                   # Parsing (comentado)
│       └── blueprint/                                # Módulos de leitura da estrutura CCNP
│           ├── __init__.py                           # Inicializa o pacote blueprint
│           ├── scanner.py                            # scan_blueprint() — lê pastas do CCNP (limpo)
│           └── scanner_commented.py                  # scan_blueprint() (comentado)
│
├── data/                                             # 📊 Dados organizados por estágio
│   ├── raw/                                          # Dados brutos (imutáveis — nunca editar)
│   │   └── raw_git_log.txt                           # Snapshot do histórico git
│   ├── processed/                                    # Dados tratados pelos scripts
│   │   ├── ccnp_progress.json                        # Progresso CCNP por domínio
│   │   └── git_log.csv                               # Commits processados e categorizados
│   └── external/                                     # Dados de APIs externas (Fase 4)
│
├── docs/                                             # 📄 Outputs HTML e documentação
│   ├── 01_line_chart.html                            # Output: Gráfico de linha
│   ├── 02_bar_chart.html                             # Output: Gráfico de barras
│   ├── 03_pie_chart.html                             # Output: Gráfico de pizza
│   ├── 04_dashboard_mvp.html                         # Output: Dashboard MVP
│   ├── 05_scatter_latency.html                       # Output: Scatter plot
│   ├── 06_heatmap_devices.html                       # Output: Mapa de calor
│   ├── 07_gauge_bandwidth.html                       # Output: Velocímetro de Banda
│   ├── 08_timeline_maintenance.html                  # Output: Gráfico de Gantt
│   ├── 09_dashboard_intermediario.html               # Output: Dashboard Intermediário
│   ├── 10_interactive_filters.html                   # Output: Dashboard Interativo
│   ├── 12_dashboard_progress.html                    # Output: Dashboard de Progresso CCNP
│   ├── 13_dashboard_git_log.html                     # Output: Dashboard Git Log
│   ├── 14_dashboard_git_log_modular.html             # Output: Dashboard Git Log Modular
│   ├── 15_dashboard_completo.html                    # Output: Dashboard Completo 3 abas
│   ├── 16_dashboard_completo_modular.html            # Output: Dashboard Completo Modular
│   ├── git_commit_guide.md                           # Guia de commits profissionais
│   ├── guia_versionamento.md                         # Guia de versionamento semântico
│   └── .nojekyll                                     # Configuração GitHub Pages
│
├── exemplos/                                         # 💡 Exemplos de uso (futuro)
│
├── tests/                                            # 🧪 Testes automatizados (futuro)
│
├── .gitignore                                        # Arquivos ignorados pelo Git
├── requirements.txt                                  # Dependências Python (Plotly, Pandas)
├── CHANGELOG.md                                      # Histórico de versões e mudanças
└── README.md                                         # Este arquivo - Documentação principal
```

---

### 📊 Gráficos Disponíveis

#### Fase 1 - Básicos (✅ Concluída)

| #  | Tipo      | Arquivo               | Descrição                           |
|----|-----------|-----------------------|-------------------------------------|
| 01 | Linha     | `01_line_chart.py`    | Evolução temporal de progresso      |
| 02 | Barras    | `02_bar_chart.py`     | Comparação entre categorias         |
| 03 | Pizza     | `03_pie_chart.py`     | Distribuição percentual             |
| 04 | Dashboard | `04_dashboard_mvp.py` | Dashboard com 4 gráficos integrados |

#### Fase 2 - Intermediários (✅ 100% Completa)

| #  | Tipo                 | Arquivo                           | Descrição                      |
|----|----------------------|-----------------------------------|--------------------------------|
| 05 | Scatter              | `05_scatter_latency.py`           | Correlação latência vs perda   |
| 06 | Heatmap              | `06_heatmap_devices.py`           | Utilização de dispositivos 24h |
| 07 | Gauge                | `07_gauge_bandwidth.py`           | Medidor de banda               |
| 08 | Timeline             | `08_timeline_maintenance.html`    | Janelas de manutenção          |
| 09 | Dashboard            | `09_dashboard_intermediario.html` | Dashboard intermediário        |
| 10 | Gráficos interativos | `10_interactive_filters.html`     | filtros, zoom, seleção         |

#### Fase 3 - Avançado (🔄 6/8 em andamento)

| #  | Tipo                                            | Arquivo                                | Descrição                                          |
|----|-------------------------------------------------|----------------------------------------|----------------------------------------------------|
| 11 | Leitura automática do repositório CCNP          | `11_read_progress.py`                  | Leitura e métricas do progresso CCNP               |
| 12 | Dashboard de progresso por acumulação           | `12_dashboard_progress.py`             | Dashboard de progresso por domínio                 |
| 13 | Pipeline git log → CSV → Dashboard              | `13_git_log_pipeline.py`               | Extração, parsing, CSV e dashboard em script único |
| 14 | Modularização do pipeline                       | `14_git_log_modular.py`                | Separa script 13 em módulos reutilizáveis          |
| 15 | Dashboard completo com múltiplas páginas        | `15_dashboard_completo.py`             | Dashboard com 3 abas: Resumo, Progresso, Git Log   |
| 16 | Dashboard completo modularizado                 | `16_dashboard_completo_modular.py`     | Versão modular do script 15 — scanner.py separado  |
| 17 | Métricas de progresso via API do GitHub         | em andamento                           | Coleta automática de dados via API GitHub          |
| 18 | GitHub Actions — atualização automática         | em andamento                           | Pipeline automático de geração do dashboard        |

### 🎨 Padrão de Organização

Cada gráfico possui **duas versões**:

- **Versão limpa** (`XX_nome.py`): Código profissional e conciso
- **Versão comentada** (`XX_nome_commented.py`): Código didático com explicações linha a linha

---

## 📦 Instalação

Pré-requisitos  
  
Python 3.8 ou superior  
pip (gerenciador de pacotes Python)  

Passos  

```bash
# 1. Clone o repositório
git clone https://github.com/alcancil/dashboards.git
cd dashboards

# 2. (Opcional) Crie ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

---

## 🚀 Como Usar

Executar Exemplos Básicos  

**Gráfico de linha (versão limpa)**  

python src/basico/01_line_chart.py  
  
**Gráfico de linha (versão comentada - didática)**  

python src/basico/01_line_chart_commented.py

**Executar Dashboard Completo (scripts 15 e 16)**

```bash
# Script 15 — monolítico (toda a lógica em um único arquivo)
python src/avancado/15_dashboard_completo.py \
  --repo "D:\ESTUDOS\CISCO\CISCO" \
  --ccnp "D:\ESTUDOS\CISCO\CISCO\CCNP 350-401 ENCOR"

# Script 16 — modular (importa extract.py, parser.py e scanner.py)
python src/avancado/16_dashboard_completo_modular.py \
  --repo "D:\ESTUDOS\CISCO\CISCO" \
  --ccnp "D:\ESTUDOS\CISCO\CISCO\CCNP 350-401 ENCOR"
```

**Visualizar resultado**  
Abrir `docs/15_dashboard_completo.html` ou `docs/16_dashboard_completo_modular.html` no navegador.  
  
Os gráficos são salvos na pasta `docs/` como arquivos HTML interativos.  
  
---  

## 🌐 Visualização Online

Os gráficos estão disponíveis online via GitHub Pages:

- [Gráfico de Linha - Progresso Semanal](https://alcancil.github.io/dashboards/01_line_chart.html)
- [Gráfico de Barras - Domínios CCNP](https://alcancil.github.io/dashboards/02_bar_chart.html)
- [Gráfico de Pizza - Distribuição por Categoria](https://alcancil.github.io/dashboards/03_pie_chart.html)
- [Dashboard MVP - Monitoramento de Rede](https://alcancil.github.io/dashboards/04_dashboard_mvp.html)
- [Gráfico Scatter (Dispersão) - latência (ms) vs perda de pacotes (%)](https://alcancil.github.io/dashboards/05_scatter_latency.html)
- [Heatmap - Utilização de Dispositivos](https://alcancil.github.io/dashboards/06_heatmap_devices.html)
- [Gauge - Monitoramento de Banda](https://alcancil.github.io/dashboards/07_gauge_bandwidth.html)
- [Timeline - Janelas de Manutenção](https://alcancil.github.io/dashboards/08_timeline_maintenance.html)
- [Dashboard Intermediário](https://alcancil.github.io/dashboards/09_dashboard_intermediario.html)
- [Dashboard Interativo com Filtros](https://alcancil.github.io/dashboards/10_interactive_filters.html)
- [Dashboard de Progresso CCNP](https://alcancil.github.io/dashboards/12_dashboard_progress.html)
- [Git Log Dashboard — Análise de Commits CCNP](https://alcancil.github.io/dashboards/13_dashboard_git_log.html)
- [Dashboard Completo CCNP ENCORE — 3 abas](https://alcancil.github.io/dashboards/15_dashboard_completo.html)
- [Dashboard Completo Modular CCNP ENCORE](https://alcancil.github.io/dashboards/16_dashboard_completo_modular.html) ⭐ **NOVO**

---

## Arquivos de Configuração  

| Arquivo          | Propósito                          | Quando Editar                                   |
|------------------|------------------------------------|-------------------------------------------------|
| requirements.txt | Lista de dependências Python       | Ao adicionar nova biblioteca                    |
| .gitignore       | Arquivos/pastas ignorados pelo Git | Ao querer ignorar novos tipos de arquivo        |
| CHANGELOG.md     | Histórico de versões e mudanças    | A cada nova versão/release                      |
| README.md        | Documentação principal do projeto  | Ao adicionar funcionalidades ou mudar estrutura |

---

## Pastas Principais

**src/ - Código-Fonte**  

Contém todos os scripts Python organizados por nível de complexidade:
  
- **basico/**: Scripts introdutórios do Plotly. Cada exemplo existe em duas versões:
  - Versão limpa (XX_nome.py) - código enxuto para produção
  - Versão comentada (XX_nome_commented.py) - código didático linha a linha
- **intermediario/**: Gráficos avançados com interatividade e automação de leitura de dados.
- **avancado/**: Dashboards com integração a dados reais, pipeline git log e leitura do blueprint CCNP.

**scripts/ - Pipeline de Dados**  

Scripts responsáveis pela transformação e geração de dados, organizados em pacotes Python:

- **parsing/git_log/**: Extrai e processa o histórico git (`extract.py` + `parser.py`)
- **parsing/blueprint/**: Lê a estrutura de pastas do repositório CCNP (`scanner.py`)
- Cada pacote possui versão limpa e comentada de seus módulos

**data/ - Dados**  
  
Organizada em três camadas seguindo padrão de engenharia de dados:

- **raw/**: Dados brutos e imutáveis — nunca editar diretamente. Fonte da verdade.
- **processed/**: Dados tratados pelos scripts de parsing (`git_log.csv`, `ccnp_progress.json`).
- **external/**: Dados vindos de APIs externas (Fase 4).
  
**docs/ - Documentação e Outputs**  
  
- Arquivos HTML gerados pelos scripts (dashboards interativos)
- Guias adicionais (Git, versionamento, etc.)

**tests/ - Testes**

- Testes automatizados (planejado para Fase 4)

---
  
## 🔄 Workflow Git Profissional

Este projeto segue Conventional Commits para manter histórico limpo e semântico.  
  
**Guidelines de Commit**  

Para guia completo com exemplos e templates, consulte:  

- 📖 docs/GIT_COMMIT_GUIDE.md
  
**Quick Reference**  

```bash
# Formato básico
<tipo>(<escopo>): <descrição>

# Exemplos:
feat(basico): add bar chart with domain comparison
fix(dashboard): correct color palette loading
docs(readme): improve structure section formatting
chore(deps): update plotly to 5.18.0
```

**Tipos Principais**  
  
- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **docs**: Mudanças na documentação
- **style**: Formatação de código
- **refactor**: Refatoração
- **test**: Adição de testes
- **chore**: Manutenção

---  

## 🗓️ Roadmap

✅ **Fase 1: Fundamentos (Semana 1)**  
  
✓ Setup do projeto e estrutura de pastas  
✓ Documentação inicial (README, CHANGELOG, Git Guide)  
✓ Gráfico de linha (versões limpa e comentada)  
✓ Gráfico de barras (versões limpa e comentada)  
✓ Gráfico de pizza (versões limpa e comentada)  
✓ Dashboard MVP com 4 gráficos  
✓ Guia de Versionamento Semântico  
  
**Status:** 7/7 completo (100%) ✅  
**Versão:** v0.2.0  
**Data de conclusão:** 12/02/2026

📅 **Fase 2: Intermediário (Semana 2)**  

✓ Gráfico scatter ( dispersão - latência vs perda de pacotes)  
✓ Heatmap (utilização de dispositivos ao longo do tempo)  
✓ Gauge (medidor de banda - velocímetro)  
✓ Timeline (janelas de manutenção)  
✓ Dashboard intermediário com filtros interativos  
✓ Gráficos interativos (filtros, zoom, seleção)  

**Status:** 6/6 completo (100%) ✅  
**Versão atual:** v0.8.0  
**Versão esperada:** v0.3.0 - v0.8.0  
**Previsão:** Semanas 2-4
  
📅 **Fase 3: Avançado (Semana 3)** 🔄  

✓ Leitura automática do repositório CCNP ⭐  
✓ Dashboard de progresso v2 — métricas por acumulação ⭐  
✓ Pipeline git log → CSV → Dashboard (script único) ⭐  
✓ Modularização do pipeline (extract.py + parser.py + orquestrador) ⭐  
✓ Dashboard completo com 3 abas (Resumo, Progresso CCNP, Git Log) ⭐  
✓ Dashboard completo modularizado (scanner.py + orquestrador modular) ⭐  
⎕ Métricas de progresso via API do GitHub  
⎕ GitHub Actions — atualização automática do dashboard  

**Status:** 6/8 completo (75%) ✅  
**Versão atual:** v0.14.0  
**Versão esperada:** v0.9.0 - v0.16.0  
**Previsão:** Semanas 3-5
  
🚀 **Fase 4: Automação (Semana 4) - PLANEJADO**  
  
⎕ GitHub Actions para auto-update  
⎕ Deploy automático do dashboard  
⎕ Testes automatizados  
⎕ Release v1.0.0  

📈 **Progresso Atual**  

| Métrica               | Valor      |
|-----------------------|------------|
| Scripts criados       | 35         |
| Gráficos gerados      | 15         |
| Commits profissionais | 30         |
| Última atualização    | 03/03/2026 |

---  

## 🤝 Contribuindo

Este é um projeto de aprendizado pessoal, mas sugestões são bem-vindas!
  
**Fork o projeto**  

- Crie uma branch de feature **(git checkout -b feature/nova-funcionalidade)**
- Commit suas mudanças **(git commit -m 'feat: adiciona nova funcionalidade')**
- Push para a branch **(git push origin feature/nova-funcionalidade)**
- Abra um Pull Request

---  

## 📝 Changelog

Veja CHANGELOG.md para histórico detalhado de versões.

---

## 📄 Licença

MIT License - Alexandre Lavorenti Cancilieri  
Você é livre para usar, modificar e distribuir este projeto.  

---

## 📧 Contato

- Alexandre Lavorenti Cancilieri
  
- GitHub: @alcancil
- LinkedIn: alexandre-analista-de-ti
- Email: <alcancil@gmail.com>

---

## 🔗 Repositório Principal

Este dashboard complementa o repositório principal de labs CCNP:  
🔗 **github.com/alcancil/ccnp-enterprise-lab**

<div align="center">  
Se este projeto te ajudou, considere dar uma ⭐!
</div>  
