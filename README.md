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
├── src/                           # Código-fonte organizado por nível
│   │
│   ├── basico/                    # 📘 Exemplos básicos Plotly
│   │   ├── 01_line_chart.py                # Gráfico de linha (limpo)
│   │   ├── 01_line_chart_commented.py      # Gráfico de linha (comentado)
│   │   ├── 02_bar_chart.py                 # Gráfico de barras (limpo)
│   │   ├── 02_bar_chart_commented.py       # Gráfico de barras (comentado)
│   │   └── README.md                       # Documentação dos exemplos
│   │
│   ├── intermediario/             # 📗 Gráficos intermediários
│   │   ├── 05_interactive.py               # Gráficos com filtros/zoom
│   │   ├── 06_auto_reader.py               # Leitura automática de dados
│   │   └── 07_ccnp_progress.py             # Dashboard de progresso CCNP
│   │
│   └── avancado/                  # 📕 Dashboard completo
│       ├── 08_full_dashboard.py            # Dashboard final integrado
│       ├── 09_kpi_metrics.py               # Métricas e KPIs de negócio
│       └── 10_netmiko_integration.py       # Integração com scripts
│
├── data/                          # 📊 Dados dos labs
│   ├── ccnp_labs.json                      # Contagem de labs por domínio
│   ├── weekly_progress.csv                 # Progresso semanal
│   └── file_stats.json                     # Estatísticas de arquivos
│
├── docs/                          # 📄 Outputs HTML e documentação
│   ├── 01_line_chart.html                  # Gráfico de linha (saída)
│   ├── 02_bar_chart.html                   # Gráfico de barras (saída)
│   └── GIT_COMMIT_GUIDE.md                 # Guia de commits profissionais
│
├── examples/                      # 💡 Exemplos de uso e tutoriais
│   └── how_to_run.md                       # Guia de execução
│
├── tests/                         # 🧪 Testes (futuro)
│
├── .gitignore                     # Arquivos ignorados pelo Git
├── requirements.txt               # Dependências Python
├── CHANGELOG.md                   # Histórico de mudanças
└── README.md                      # Este arquivo
```

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
- [Dashboard MVP - Monitoramento de Rede**](https://alcancil.github.io/dashboards/04_dashboard_mvp.html) ⭐ **NOVO**

**Base URL:** https://alcancil.github.io/dashboards/  

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
✓ Dashboard MVP com 4 gráficos ⭐
✓ Guia de Versionamento Semântico ⭐  
  
**Status:** 7/7 completo (100%) ✅  
**Versão:** v0.2.0
**Data de conclusão:** 12/02/2026

📅 **Fase 2: Intermediário (Semana 2) - PLANEJADO**  

⎕ Gráficos interativos (filtros, zoom, seleção)  
⎕ Leitura automática do repositório CCNP  
⎕ Dashboard de progresso por domínio  
⎕ Integração com dados CSV/JSON  
  
📅 **Fase 3: Avançado (Semana 3) - PLANEJADO**
  
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
| Scripts criados       | 2          |
| Gráficos gerados      | 1          |
| Commits profissionais | 5          |
| Última atualização    | 12/10/2025 |

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
- Email: alcancil@gmail.com

### 🔗 Repositório Principal

Este dashboard complementa o repositório principal de labs CCNP:  
🔗 **github.com/alcancil/ccnp-enterprise-lab**

<div align="center">  
Se este projeto te ajudou, considere dar uma ⭐!
</div>  
