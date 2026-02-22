# CCNP Lab Dashboard 📊

Dashboard interativo para visualização de progresso nos estudos CCNP Enterprise.

## 🎯 Objetivos do Projeto  

Este repositório documenta minha jornada de aprendizado prático, combinando três objetivos:

- Aprender Plotly - Do básico ao avançado, criando visualizações interativas
- Dashboard Profissional - Painel para acompanhar progresso dos 80+ labs CCNP
- Git Workflow - Praticar versionamento profissional com commits semânticos
- Integração - Conectar com scripts de automação (Netmiko/Paramiko)

## 📁 Estrutura do Projeto  

```bash
dashboards/
│
├── src/                                            # Código-fonte organizado por nível
│   │
│   ├── basico/                                     # 📘 Gráficos básicos e fundamentos
│   │   ├── 01_line_chart.py                        # Gráfico de linha (limpo)
│   │   ├── 01_line_chart_commented.py              # Gráfico de linha (comentado)
│   │   ├── 02_bar_chart.py                         # Gráfico de barras (limpo)
│   │   ├── 02_bar_chart_commented.py               # Gráfico de barras (comentado)
│   │   ├── 03_pie_chart.py                         # Gráfico de pizza (limpo)
│   │   ├── 03_pie_chart_commented.py               # Gráfico de pizza (comentado)
│   │   ├── 04_dashboard_mvp.py                     # Dashboard MVP (limpo)
│   │   └── 04_dashboard_mvp_commented.py           # Dashboard MVP (comentado)
│   │
│   ├── intermediario/                              # 📗 Gráficos intermediários
│   │   ├── 05_scatter_latency.py                   # Scatter: latência vs perda
│   │   ├── 05_scatter_latency_commented.py         # Scatter (comentado)
│   │   ├── 06_heatmap_devices.py                   # Heatmap: utilização 24h
│   │   ├── 06_heatmap_devices_commented.py         # Heatmap (comentado)
│   │   ├── 07_gauge_bandwidth.py                   # Gauge (Velocímetro) - Monitoramento de Banda (Limpo)       
│   │   ├── 07_gauge_bandwidth_commented.py         # Gauge - Monitoramento de Banda (comentado)
│   │   ├── 08_timeline_maintenance.py              # Timeline - Gráfico da Gantt - Janela de manutenção (Limpo) 
│   │   ├── 08_timeline_maintenance_commented.py    # Timeline - Gráfico da Gantt - Janela de manutenção (Comentado)
│   │   ├── 09_dashboard_intermediario.py           # Dashboard Intermediario (limpo)
│   │   ├── 09_dashboard_intermediario_commented.py # Dashboard Intermediario (Comentado)
│   │   ├── 10_interactive_filters.py               # Dashboard Interativo (limpo) 
│   │   └── 10_interactive_filters_commented.py     # Dashboard Interativo (comentado)
│   │
│   └── avancado/                                   # 📕 Dashboards avançados (futuro)
│       └── (em desenvolvimento)
│
├── data/                                           # 📊 Dados para processamento (futuro)
│
├── docs/                                           # 📄 Outputs HTML e documentação
│   ├── 01_line_chart.html                          # Output: Gráfico de linha
│   ├── 02_bar_chart.html                           # Output: Gráfico de barras
│   ├── 03_pie_chart.html                           # Output: Gráfico de pizza
│   ├── 04_dashboard_mvp.html                       # Output: Dashboard MVP
│   ├── 05_scatter_latency.html                     # Output: Scatter plot
│   ├── 06_heatmap_devices.html                     # Output: Mapa de calor
│   ├── 07_gauge_bandwidth.html                     # Output: Velocímetro - Monitoramento de Banda
│   ├── 08_timeline_maintenance.html                # Output: Gráfico de Gantt - Janela de Manutenção
│   ├── 09_dashboard_intermediario.html             # Output: Dashboard Intermediario
│   ├── 10_interactive_filters.html                 # Output: Dashboard Interativo
│   ├── git_commit_guide.md                         # Guia de commits profissionais
│   ├── guia_versionamento.md                       # Guia de versionamento semântico
│   └── .nojekyll                                   # Configuração GitHub Pages
│
├── exemplos/                                       # 💡 Exemplos de uso (futuro)
│
├── testes/                                         # 🧪 Testes automatizados (futuro)
│
├── .gitignore                                      # Arquivos ignorados pelo Git
├── requerimentos.txt                               # Dependências Python (Plotly, Pandas)
├── CHANGELOG.md                                    # Histórico de versões e mudanças
└── README.md                                       # Este arquivo - Documentação principal
```

### 📊 Gráficos Disponíveis

#### Fase 1 - Básicos (✅ Concluída)

| #  | Tipo      | Arquivo               | Descrição                           |
|----|-----------|-----------------------|-------------------------------------|
| 01 | Linha     | `01_line_chart.py`    | Evolução temporal de progresso      |
| 02 | Barras    | `02_bar_chart.py`     | Comparação entre categorias         |
| 03 | Pizza     | `03_pie_chart.py`     | Distribuição percentual             |
| 04 | Dashboard | `04_dashboard_mvp.py` | Dashboard com 4 gráficos integrados |

#### Fase 2 - Intermediários (🚧 50% Completa)

| #  | Tipo                 | Arquivo                           | Descrição                      |
|----|----------------------|-----------------------------------|--------------------------------|
| 05 | Scatter              | `05_scatter_latency.py`           | Correlação latência vs perda   |
| 06 | Heatmap              | `06_heatmap_devices.py`           | Utilização de dispositivos 24h |
| 07 | Gauge                | `07_gauge_bandwidth.py`           | Medidor de banda               |
| 08 | Timeline             | `08_timeline_maintenance.html`    | Janelas de manutenção          |
| 09 | Dashboard            | `09_dashboard_intermediario.html` | Dashboard intermediário        |
| 10 | Gráficos interativos | `10_interactive_filters.html`     | filtros, zoom, seleção         |

### 🎨 Padrão de Organização

Cada gráfico possui **duas versões**:

- **Versão limpa** (`XX_nome.py`): Código profissional e conciso
- **Versão comentada** (`XX_nome_commented.py`): Código didático com explicações linha a linha

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

## 🚀 Como Usar

Executar Exemplos Básicos  

**Gráfico de linha (versão limpa)**  

python src/basico/01_line_chart.py  
  
**Gráfico de linha (versão comentada - didática)**  

python src/basico/01_line_chart_commented.py
  
**Visualizar resultado**  
**Abrir: docs/01_line_chart.html no navegador**  
  
Os gráficos são salvos na pasta docs/ como arquivos HTML interativos.  
  
---  

## 🌐 Visualização Online

Os gráficos estão disponíveis online via GitHub Pages:

- [Gráfico de Linha - Progresso Semanal](https://alcancil.github.io/dashboards/01_line_chart.html)
- [Gráfico de Barras - Domínios CCNP](https://alcancil.github.io/dashboards/02_bar_chart.html)
- [Gráfico de Pizza - Distribuição por Categoria](https://alcancil.github.io/dashboards/03_pie_chart.html)
- [Dashboard MVP - Monitoramento de Rede**](https://alcancil.github.io/dashboards/04_dashboard_mvp.html)
- [Gráfico Scatter (Dispersão) - latência (ms) vs perda de pacotes (%)](https://alcancil.github.io/dashboards/05_scatter_latency.html)  
- [Gráfico Heatmap - Utilização de Dispositivos 24h](https://alcancil.github.io/dashboards/06_heatmap_devices.html)  
- [Gráfico Gauge - Monitoramento de Banda (velocímetro)](https://alcancil.github.io/dashboards/07_gauge_bandwidth.html)  
- [Gráfico Timeline (Gantt) - Janelas de Manutenção](https://alcancil.github.io/dashboards/08_timeline_maintenance.html)  
- [Dashboard Intermediario - Monitoramento de Rede**](https://alcancil.github.io/dashboards/10_interactive_filters.html)  
- [Dashboard Interativo - Monitoramento de Rede**](https://alcancil.github.io/dashboards/09_dashboard_intermediario.html) ⭐ **NOVO**  


**Base URL:** <https://alcancil.github.io/dashboards/>  

---  

## 📚 Descrição dos Arquivos

**Arquivos de Configuração**  

| Arquivo          | Propósito                          | Quando Editar                                   |
|------------------|------------------------------------|-------------------------------------------------|
| requirements.txt | Lista de dependências Python       | Ao adicionar nova biblioteca                    |
| .gitignore       | Arquivos/pastas ignorados pelo Git | Ao querer ignorar novos tipos de arquivo        |
| CHANGELOG.md     | Histórico de versões e mudanças    | A cada nova versão/release                      |
| README.md        | Documentação principal do projeto  | Ao adicionar funcionalidades ou mudar estrutura |

## Pastas Principais

**src/ - Código-Fonte**  

Contém todos os scripts Python organizados por nível de complexidade:
  
- **basico/**: Scripts introdutórios do Plotly. Cada exemplo existe em duas versões:
  - Versão limpa (XX_nome.py) - código enxuto para produção
  - Versão comentada (XX_nome_commented.py) - código didático linha a linha
- **intermediario/**: Gráficos avançados com interatividade e automação de leitura de dados.  
- **avancado/**: Dashboard completo com integração a outros sistemas e métricas de negócio.
  
**data/ - Dados**  
  
Armazena dados estruturados em formatos JSON/CSV:  

- **ccnp_labs.json**: Contagem de labs por domínio CCNP
- **weekly_progress.csv**: Histórico de progresso semanal
- **file_stats.json**: Estatísticas de arquivos do repositório principal
  
**docs/ - Documentação e Outputs**  
  
- Arquivos HTML gerados pelos scripts (dashboards interativos)
- Guias adicionais (Git, contribuição, etc)
  
**examples/ - Exemplos e Tutoriais**  

- Guias práticos de como usar o projeto, modificar gráficos, etc.
  
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

📅 **Fase 2: Intermediário (Semana 2) - PLANEJADO**  

✓ Gráfico scatter ( dispersão - latência vs perda de pacotes)  
✓ Heatmap (utilização de dispositivos ao longo do tempo)  
✓ Gauge (medidor de banda - velocímetro)  
✓ Timeline (janelas de manutenção)  
✓ Dashboard intermediário com filtros interativos  
✓ Gráficos interativos (filtros, zoom, seleção) ⭐  

**Status:** 6/6 completo (100%) ✅  
**Versão atual:** v0.8.0  
**Versão esperada:** v0.3.0 - v0.8.0  
**Previsão:** Semanas 2-4
  
📅 **Fase 3: Avançado (Semana 3) - PLANEJADO** 🔄  

⎕ Leitura automática do repositório CCNP  
⎕ Dashboard de progresso por domínio  
⎕ Integração com dados CSV/JSON  
⎕ Dashboard completo com múltiplas páginas  
⎕ Métricas de negócio e KPIs  
⎕ Integração com scripts Netmiko/Paramiko  
⎕ Observabilidade (Zabbix/Graylog)  
  
🚀 **Fase 4: Automação (Semana 4) - PLANEJADO**  
  
⎕ GitHub Actions para auto-update  
⎕ Deploy automático do dashboard  
⎕ Testes automatizados  
⎕ Release v1.0.0  

📈 **Progresso Atual**  

| Métrica               | Valor      |
|-----------------------|------------|
| Scripts criados       | 18         |
| Gráficos gerados      | 9          |
| Commits profissionais | 21         |
| Última atualização    | 20/02/2026 |

---  

## 🤝 Contribuindo

Este é um projeto de aprendizado pessoal, mas sugestões são bem-vindas!
  
**Fork o projeto**  

- Crie uma branch de feature **(git checkout -b feature/nova-funcionalidade)**
- Commit suas mudanças **(git commit -m 'feat: adiciona nova funcionalidade')**
- Push para a branch **(git push origin feature/nova-funcionalidade)**
- Abra um Pull Request

---  

### 📝 Changelog

Veja CHANGELOG.md para histórico detalhado de versões.

### 📄 Licença

MIT License - Alexandre Lavorenti Cancilieri  
Você é livre para usar, modificar e distribuir este projeto.  

### 📧 Contato

- Alexandre Lavorenti Cancilieri
  
- GitHub: @alcancil
- LinkedIn: alexandre-analista-de-ti
- Email: <alcancil@gmail.com>

### 🔗 Repositório Principal

Este dashboard complementa o repositório principal de labs CCNP:  
🔗 **github.com/alcancil/ccnp-enterprise-lab**

<div align="center">  
Se este projeto te ajudou, considere dar uma ⭐!
</div>  
