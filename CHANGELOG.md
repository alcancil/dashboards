## Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Em Desenvolvimento

- GitHub Actions — atualização automática do dashboard (Fase 4)
- Deploy automático do dashboard
- Testes automatizados
- Migração do token para GitHub Actions Secrets (segurança Nível 3)

---

## [0.15.0] - 2026-03-04

### Adicionado

- Novo pacote `scripts/collectors/` com responsabilidade única: coleta de dados externos via API
- `scripts/collectors/__init__.py`: inicializa o pacote collectors
- `scripts/collectors/github_api.py`: coleta commits, info e estatísticas dos dois repositórios via API REST do GitHub
- `scripts/collectors/github_api_commented.py`: versão didática com documentação sobre níveis de segurança (Nível 1 → Nível 3)
- Novo pacote `scripts/parsing/github/` com responsabilidade única: processamento dos dados da API
- `scripts/parsing/github/__init__.py`: inicializa o pacote github
- `scripts/parsing/github/processor.py`: transforma JSON bruto em DataFrames e CSVs estruturados
- `scripts/parsing/github/processor_commented.py`: versão didática com explicação do pipeline e decisões de design
- `src/avancado/17_github_metrics.py`: orquestrador com dashboard de 4 abas (Visão Geral, DASHBOARDS, CISCO, Correlação)
- `src/avancado/17_github_metrics_commented.py`: versão comentada com narrativa de portfólio
- `data/processed/commits_dashboards.csv`: série temporal de commits do repositório DASHBOARDS
- `data/processed/commits_cisco.csv`: série temporal de commits do repositório CISCO (2369 commits, 63 semanas)
- `data/processed/commits_all.csv`: dataset combinado dos dois repositórios para análise de correlação
- `data/processed/repo_info.json`: metadados dos repositórios (stars, forks, datas, tamanho)
- `docs/17_github_metrics.html`: dashboard com correlação entre os dois repositórios

### Alterado

- `.gitignore`: adicionado `data/raw/` — JSONs brutos são regeneráveis, não versionados
- `requirements.txt`: adicionado `requests` e `python-dotenv`
- README.md: item 17 concluído, estrutura atualizada, roadmap 7/8 (87.5%), versão v0.15.0
- CHANGELOG.md: [Unreleased] atualizado, entrada v0.15.0 adicionada

### Segurança

- Nível 1 implementado: token via `.env` + `.gitignore` (didático — narrativa de evolução)
- `data/raw/` ignorado pelo git — JSONs brutos nunca versionados (boas práticas de engenharia de dados)
- Próximo passo documentado: migrar para GitHub Actions Secrets (Nível 3) na Fase 4

### Documentação

- Estratégia de persistência: arquivo com timestamp (`github_api_YYYYMMDD_HHMMSS.json`) + `_latest` fixo
- Paginação automática: `_get_paginated()` percorre todas as páginas da API (repositório CISCO tem 2369 commits)
- `main()` inteligente: verifica se CSVs já existem antes de chamar a API — economiza rate limit
- Separação clara entre coleta (`collectors/`), processamento (`parsing/github/`) e visualização (`src/avancado/`)

---

## [0.14.0] - 2026-03-03

### Adicionado

- Novo pacote `scripts/parsing/blueprint/` com responsabilidade única: leitura da estrutura de pastas do CCNP
- `scripts/parsing/blueprint/__init__.py`: inicializa o pacote
- `scripts/parsing/blueprint/scanner.py`: função `scan_blueprint()` extraída do script 15
- `scripts/parsing/blueprint/scanner_commented.py`: versão didática com comentários detalhados
- `DOMAIN_ORDER` e `DOMAIN_COLORS` centralizados em `scanner.py` — evita duplicação entre módulo e orquestrador
- `SKIP_FOLDERS` como set (`{"Arquivos", "Imagens", "Simulado"}`) — lookup O(1) mais eficiente que lista
- `src/avancado/16_dashboard_completo_modular.py`: orquestrador modular que importa `validate_repo`, `extract_git_log` de `extract.py`, `parse_lines`, `save_csv` de `parser.py` e `scan_blueprint`, `DOMAIN_ORDER`, `DOMAIN_COLORS` de `scanner.py`
- `src/avancado/16_dashboard_completo_modular_commented.py`: versão didática com comparação explícita entre script 15 (monolítico) e script 16 (modular)

### Alterado

- README.md: item 16 concluído na tabela Fase 3, link GitHub Pages, roadmap 6/8 (75%), versão v0.14.0
- CHANGELOG.md: [Unreleased] atualizado, entrada v0.14.0 adicionada

### Documentação

- Narrativa monolítico → modular: script 15 e 16 demonstram o princípio da responsabilidade única na prática
- `scan_blueprint()` classificada como parsing porque lê uma estrutura (pastas) e transforma em dados estruturados (dicionário) — mesma responsabilidade semântica de `extract.py` e `parser.py`
- `sys.path.insert(0, BASE_DIR)` no orquestrador: necessário para que o Python encontre o pacote `scripts/` como módulo importável
- `DOMAIN_COLORS` e `DOMAIN_ORDER` importados do `scanner.py` em vez de redefinidos no orquestrador

---

## [0.13.0] - 2026-03-02

### Adicionado

- Dashboard completo com 3 abas em um único HTML (`15_dashboard_completo.py`)
- Fonte de dados dupla: git log extraído na hora via `subprocess` + estrutura de pastas via `os.listdir()`
- Dois argumentos CLI: `--repo` (raiz do `.git`) e `--ccnp` (pasta do blueprint ENCORE)
- Função `scan_blueprint()`: escaneia os 6 domínios do Blueprint ENCORE e coleta tópicos, subtópicos e labs por pasta
- Detecção de labs por nome de pasta: qualquer pasta com `"Exemplo Pr"` no nome é contabilizada como lab
- Ignoração automática de pastas de suporte: `Arquivos`, `Imagens`, `Simulado`
- Sistema de abas com HTML/CSS/JS puro — sem dependências externas além do Plotly
- `plotly.io.to_html(full_html=False, include_plotlyjs=False)` para embutir múltiplos gráficos sem duplicar o JS
- **Aba 1 — Resumo Geral**: 4 cards (commits, subtópicos, labs, domínios iniciados) + barras horizontais por domínio + linha de commits por semana
- **Aba 2 — Progresso CCNP**: barras agrupadas (subtópicos vs labs), pizza/donut de distribuição + tabela HTML com status por domínio
- **Aba 3 — Análise de Commits**: 4 cards + grade 2x2 (linha, barras por ação, barras por domínio, heatmap)
- Arquivos `src/avancado/15_dashboard_completo.py` (versão limpa) e `src/avancado/15_dashboard_completo_commented.py` (versão didática)

### Alterado

- README.md: item 15 concluído na tabela Fase 3, link GitHub Pages, roadmap 5/8 (62.5%), versão v0.13.0
- CHANGELOG.md: [Unreleased] atualizado, entrada v0.13.0 adicionada

### Documentação

- Comentários sobre `scan_blueprint()`: `os.listdir()`, `sorted()`, filtragem de pastas de suporte, detecção de labs por substring
- Diferença entre fonte de dados: estrutura de pastas (o que existe) vs git log (quando e como foi trabalhado)
- `pio.to_html(full_html=False)`: por que não embutir o JS do Plotly N vezes
- Sistema de abas: `display:none` / `display:block` via JS puro sem dependência de framework
- `specs=[[ {"type":"xy"}, {"type":"domain"} ]]`: obrigatório ao misturar gráfico cartesiano com Pie no mesmo subplot

---

## [0.11.0] - 2026-02-28

### Adicionado

- Pipeline completo git log → CSV → Dashboard em script único (`13_git_log_pipeline.py`)
- 4 etapas sequenciais dentro de um único script (didático — antes de modularizar):
  - `[1/4]` Extração: executa `git log --pretty=format:"%H|%ad|%s" --date=iso` via `subprocess` e salva em `data/raw/raw_git_log.txt`
  - `[2/4]` Parsing: separa campos pelo delimitador `|`, normaliza verbos e classifica commits por ação, domínio CCNP e lab
  - `[3/4]` CSV: salva registros estruturados em `data/processed/git_log.csv` com 8 colunas
  - `[4/4]` Dashboard: lê o CSV com Pandas e gera `docs/13_dashboard_git_log.html` com 4 gráficos
- Argumento `--repo` via `argparse` para portabilidade entre máquinas (sem path hardcoded)
- Validação do repositório antes da execução (verifica diretório e pasta `.git`)
- `BASE_DIR` via `__file__` para caminhos sempre relativos à raiz do projeto
- Parsing sem regex — apenas `split()`, `strip()`, `lower()` e operador `in`:
  - `extract_action()` — normaliza verbo de ação via dicionário `ACTION_MAP` (trata typos reais: `alteradoo`, `aletardo`, `alterad`, etc.)
  - `extract_domain()` — identifica domínio CCNP por palavras-chave (`ospf`, `bgp`, `vrf`, `python`, `vpn`, etc.)
  - `extract_lab()` — detecta commits de laboratório pela presença de `"Exemplo Prático"` na mensagem
- Dashboard com 4 gráficos e tema escuro estilo terminal:
  - `[1,1]` Linha com área preenchida: commits ao longo do tempo por semana
  - `[1,2]` Barras com cor por tipo de ação: distribuição de verbos normalizados
  - `[2,1]` Barras horizontais: distribuição por domínio CCNP
  - `[2,2]` Heatmap estilo GitHub contributions: commits por dia da semana vs semana
  - 4 cards informativos no topo: Total de Commits, Primeiro Commit, Último Commit, Labs Realizados
- CSV com 8 colunas: `hash`, `date`, `week`, `weekday`, `message`, `action`, `domain`, `lab`
- Arquivo `src/avancado/13_git_log_pipeline.py` (versão limpa)
- Arquivo `src/avancado/13_git_log_pipeline_commented.py` (versão didática com comentários linha a linha)

### Alterado

- `requirements.txt` atualizado: adicionado `pandas` como dependência core
- README.md atualizado: script 13 na tabela Fase 3, link no GitHub Pages, roadmap atualizado
- Roadmap Fase 3: item 13 marcado como concluído, novo item 14 (modularização) adicionado
- Numeração dos itens pendentes da Fase 3 ajustada (14→18)

### Documentação

- Comentários detalhados sobre `argparse` e argumentos de linha de comando
- Uso de `subprocess.run` com lista de argumentos para portabilidade
- `BASE_DIR` com `os.path.dirname` e `__file__` para caminhos independentes de CWD
- Filosofia de parsing sem regex: legibilidade vs poder expressivo
- Dicionário de lookup como alternativa ao pattern matching
- Operador `in` para busca de substring em mensagens de commit
- `csv.DictWriter` para exportação estruturada
- `pandas` para leitura de CSV e agregações (`groupby`, `value_counts`, `unstack`)
- Heatmap com `pivot table`, `reindex` e transposição de matriz (`.values.T`)
- Annotations do Plotly para cards informativos fora da área de subplots

---

## [0.10.1] - 2026-02-26

### Alterado

- Reestruturação arquitetural da pasta `data/` em três camadas:
  - `data/raw/` — dados brutos e imutáveis (fonte da verdade)
  - `data/processed/` — dados tratados pelos scripts de pipeline
  - `data/external/` — reservado para APIs externas (Fase 4)
- Criação da pasta `scripts/` com subpastas `parsing/`, `metrics/` e `integrations/`
  - Separa scripts de pipeline de dados dos scripts de visualização em `src/`
  - Padrão de engenharia de dados: raw → processed → dashboard
- Renomeação de `testes/` para `tests/` (padronização para inglês)
- Arquivo `ccnp_progress.json` movido de `data/` para `data/processed/`

### Corrigido

- Caminho do JSON nos scripts 11 e 12 atualizado para `data/processed/`
  - `11_read_progress.py` e `11_read_progress_commented.py`
  - `12_dashboard_progress.py` e `12_dashboard_progress_commented.py`
- Removido `read_progress_helper.py` (descontinuado — scripts 11 e 12 são autossuficientes)

### Documentação

- README.md atualizado com nova estrutura de pastas
- Seção "Pastas Principais" reescrita para refletir arquitetura de pipeline
- Roadmap Fase 3 corrigido: versão atual v0.10.1, range v0.9.0 - v0.15.0
- Tabela Fase 3 atualizada: script 12 marcado como concluído, item 13 descreve pipeline

---

### [0.10.0] - 2026-02-23

## Adicionado

- Dashboard de Progresso CCNP v2 — Métricas por Acumulação
- Abordagem v2: mede conteúdo acumulado (não % de total desconhecido)
- Ideal para repositórios em construção contínua sem backlog pré-definido
- Dashboard HTML com 6 subplots em grade 2x3:
  - [1,1] Barras empilhadas: conteúdo acumulado por domínio (teoria + labs + resumo)
  - [1,2] Barras simples: labs realizados por domínio (cinza para não iniciados)
  - [1,3] Donut chart: distribuição proporcional entre teoria, labs e resumo
  - [2,1] Barras com colorscale: total acumulado (gradiente cinza → azul → verde)
  - [2,2] Comparativo: teoria vs labs por domínio
  - [2,3] Tabela: resumo completo com zebra striping e status ✅/⬜
- Cards de totais no topo via annotations (teoria, labs, resumo, total geral)
- Tema escuro estilo terminal (Courier New, fundo #0F1117)
- Cores condicionais: domínios não iniciados aparecem em cinza
- Arquivo read_progress_helper.py — módulo compartilhado de leitura e cálculo
- Centraliza carregar_dados e calcular_metricas_gerais
- Importado pelos scripts 11 e 12 (e futuros scripts da Fase 3)
- Quando a API GitHub entrar (Fase 4), só este arquivo muda
- Arquivo `12_dashboard_progress.py` (versão limpa)
- Arquivo `12_dashboard_progress_commented.py` (versão didática com comentários linha a linha)
- Item Dashboard de progresso por domínio do roadmap concluído

## Documentação

- Diferença explícita entre abordagem v1 (script 11) e v2 (script 12):
  - v1: total/concluidos → percentual de um plano fixo (escopo fechado)
  - v2: concluidos como valor absoluto → acumulação (construção contínua)
- Arquitetura de módulos: helper → scripts 11 e 12
- Colorscale numérica em barras (cor proporcional ao valor)
- Donut chart com hole=0.45
- Loop sobre lista de tuplas para annotations sem repetição de código
- Zebra striping com fill_color e multiplicação de lista

## Alterado

- README.md atualizado: script 12, helper, roadmap Fase 3 (2/8, v0.10.0)
- Seção [Unreleased] atualizada: removidos itens concluídos

---

## [0.9.0] - 2026-02-22

### Adicionado

- Leitura e Métricas do Progresso CCNP — primeiro script da Fase 3 (Avançado)
- Lê data/ccnp_progress.json e calcula métricas por domínio e totais gerais
- Cobre os 6 domínios do CCNP ENCORE 350-401:
  - Architecture, Virtualization, Infrastructure, Network Assurance, Security, Automation
- Três tipos de atividade rastreados por tópico: teoria, labs e resumo
- Métricas calculadas por tópico, por domínio e geral:
  - Totais planejados e concluídos
  - Percentual de conclusão
  - Dias restantes até a meta
- Barra de progresso visual no terminal (█░) por domínio
- Identificação automática de domínios não iniciados
- Arquitetura em três camadas separadas:
  - Leitura (carregar_dados)
  - Cálculo (calcular_metricas_topico, calcular_metricas_dominio, calcular_metricas_gerais)
  - Exibição (exibir_resumo, gerar_barra)
- Projetado para ser importado como módulo pelo script 12 (dashboard visual)
- Compatível com Windows, Linux e Mac via os.path.join
- Arquivo data/ccnp_progress.json com dados reais do repositório CCNP
- Schema estruturado em: repositório → domínios → tópicos → teoria/labs/resumo
- Campos ultima_atualizacao e meta_conclusao para rastreamento temporal
- Dados iniciais: 70 aulas de teoria, 19 labs, 1 resumo concluídos
- Arquivo src/avancado/11_read_progress.py (versão limpa)
- Arquivo src/avancado/11_read_progress_commented.py (versão didática com comentários linha a linha)
- Pasta data/ criada na raiz do repositório
- Pasta src/avancado/ criada para scripts da Fase 3
- Início da Fase 3 - Avançado do roadmap

### Alterado

- README.md atualizado com estrutura da Fase 3 e link para o script 11
- Roadmap atualizado: item "Leitura automática do repositório CCNP" marcado como concluído
- Seção [Unreleased] atualizada com itens restantes da Fase 3

### Documentação

- Comentários detalhados sobre leitura de JSON com json.load()
- Uso de os.path.join() para caminhos portáveis entre sistemas operacionais
- Proteção contra KeyError com .get() e valores padrão
- Cálculo de diferença entre datas com datetime e timedelta
- Padrão if __name__ == '__main__' para permitir importação como módulo
- Separação de responsabilidades: leitura, cálculo e exibição em funções distintas
- Variações possíveis: velocidade de progresso, projeção de conclusão, exportação CSV

---

## [0.8.0] - 2026-02-22

### Adicionado

- **Gráfico Interativo** com Filtros Linkados para análise de latência e performance de links
  - Dois subplots linkados em layout 60/40:
    - **Scatter Plot (esquerda)**: latência vs perda de pacotes com 100 links simulados
    - **Box Plot (direita)**: distribuição estatística de latência por tipo de link
  - Tamanho dos pontos proporcional ao bandwidth do link (terceira dimensão visual)
  - Zona de performance ótima destacada no scatter (< 50ms, < 2% perda)
  - Três controles interativos implementados com Plotly puro (sem Dash):
    - Dropdown (região): filtra dados em ambos os subplots simultaneamente
    - Botões Toggle (tipo de link): mostra/oculta séries individualmente
    - Range Slider (latência): ajusta faixa de latência visível no scatter
- legendgroup vinculando scatter e box: clique na legenda oculta ambos
- Características realistas por tipo de link:
  - Fibra: 5-30ms latência, 0-1% perda, 500-1000 Mbps
  - Wireless: 15-80ms latência, 0.5-5% perda, 50-300 Mbps
  - MPLS: 10-50ms latência, 0-2% perda, 200-600 Mbps
  - Internet: 30-150ms latência, 1-8% perda, 10-100 Mbps
- 5 regiões do Brasil disponíveis no filtro dropdown
- boxmean='sd' exibindo média e desvio padrão no box plot
- Arquivo `10_interactive_filters.py` (versão limpa)
- Arquivo `10_interactive_filters_commented.py` (versão didática com comentários linha a linha)
- Item Filtros dropdown interativos da seção [Unreleased] concluído

### Corrigido

- **Bug no filtro dropdown de região:** box plot desaparecia ao selecionar qualquer região  
- **Causa:** restyle com listas concatenadas causava aplicação incorreta dos dados quando scatter e box tinham tamanhos de lista diferentes por região
- **Solução:** separação em dois pares [dados, índices] via args e args2, direcionando scatter (índices 0-3) e box (índices 4-7) de forma independente

### Alterado

- README.md atualizado com link para o novo gráfico interativo
- Roadmap atualizado com item de filtros interativos marcado como concluído
- Seção [Unreleased] atualizada: removidos itens concluídos

### Documentação

- Comentários detalhados sobre os três métodos de interatividade do Plotly puro:
  - restyle: substitui dados dos traces (x, y, text, marker.size)
  - relayout: altera propriedades do layout (range de eixos)
  - update: controla visibilidade dos traces
- Explicação de indices explícitos no restyle para evitar interferência entre grupos
- Uso de legendgroup para vincular traces de subplots diferentes
- Diferença entre Plotly puro (HTML estático) e Dash (servidor + callbacks)
- Variações possíveis (reset zoom, trendline, exportação como imagem)

---

## [0.7.0] - 2026-02-21

### Adicionado

- **Dashboard Intermediário integrando 4 gráficos** com controles interativos
  - Grid 2x2 com tipos heterogêneos de gráfico em um único dashboard
  - **Scatter Plot** (Latência vs Perda de Pacotes):
    - 50 links simulados com características realistas por tipo
    - Fibra: 5-30ms latência, 0-1% perda
    - Wireless: 15-80ms latência, 0.5-5% perda
    - MPLS: 10-50ms latência, 0-2% perda
    - Internet: 30-150ms latência, 1-8% perda
    - Cores distintas por tipo de link com legenda global
  - **Heatmap** (Utilização de Dispositivos 24h):
    - Matriz 6x24 (6 dispositivos × 24 horas)
    - Padrão realista de tráfego (madrugada/ramp-up/comercial/noite)
    - Overhead extra em Firewalls (+10-20%) por stateful inspection
    - Escala de cor verde → laranja → vermelho
  - **Gauge Indicator** (Utilização Média de Banda):
    - Média calculada dos 4 links principais
    - Zonas coloridas: Verde (0-50%), Amarelo (50-80%), Vermelho (80-100%)
    - Threshold visual em 90% (linha vermelha)
  - **Tabela de Status (Resumo dos Links):**
    - Capacidade e utilização absoluta e percentual de cada link
    - Semáforo de status com emojis (🟢🟡🔴)
    - Zebra striping para facilitar leitura
- Timestamp dinâmico de atualização no título
- Legenda global horizontal posicionada no topo direito
- Arquivo `09_dashboard_intermediario.py` (versão limpa)
- Arquivo `09_dashboard_intermediario_commented.py` (versão didática com comentários linha a linha)
- Quinta e última entrega da Fase 2 - Gráficos Intermediários (100% completo)

### Alterado

- README.md atualizado com link para o novo dashboard intermediário
- Roadmap da Fase 2 marcado como 100% completo (5/5 tarefas)
- Seção [Unreleased] atualizada: removidos itens concluídos (Timeline e Dashboard Intermediário)

### Documentação

- Comentários detalhados sobre dashboards com subplots de tipos mistos
- Explicação da diferença entre figure_factory e graph_objects
- Uso de specs em make_subplots() para tipos heterogêneos (scatter, heatmap, indicator, table)
- Lógica de semáforo com expressão condicional encadeada
- Zebra striping em tabelas com multiplicação de lista
- Variações possíveis (5º subplot com colspan, real-time com Dash, múltiplos gauges)
- Aplicações práticas em NOC/SOC e relatórios de SLA

---

## [0.6.0] - 2026-10-20

### Adicionado

- **Gráfico Timeline** para visualização de janelas de manutenção programadas
  - Implementa diagrama de Gantt (cronograma) para 90 dias
  - Monitora 10 dispositivos de infraestrutura crítica
  - Gera ~25-30 manutenções distribuídas ao longo do tempo
  - 5 tipos de manutenção com cores distintas:
    - Upgrade Firmware (Azul)
    - Backup Config (Verde)
    - Análise Performance (Laranja)
    - Manutenção Preventiva (Roxo)
    - Substituição HW (Vermelho)
  - Duração variável: 2-8 horas por manutenção
  - Tooltips com data/hora de início e fim formatadas
  - Agrupamento automático por dispositivo
  - Grade temporal para fácil identificação de períodos
  - Estatísticas exibidas (total, por tipo, período)
- Arquivo `08_timeline_maintenance.py` (versão limpa)
- Arquivo `08_timeline_maintenance_commented.py` (versão didática com comentários linha a linha)
- Quarto gráfico da **Fase 2 - Gráficos Intermediários** (80% completo)
- Dependência numpy adicionada ao projeto (requerida pelo figure_factory)

### Alterado

- README.md atualizado com link para o novo gráfico timeline
- Roadmap da Fase 2 marcado como 80% completo (4/5 tarefas)
- Arquivo `requerimentos.txt` atualizado com numpy>=1.24.0

### Documentação

- Comentários detalhados sobre gráficos Gantt/Timeline
- Exemplos de planejamento de manutenções
- Explicação de figure_factory e create_gantt()
- Trabalho com datetime e timedelta
- Variações possíveis (milestones, dependências, agrupamentos)
- Aplicações práticas em change management e planejamento

---

## [0.5.0] - 2026-02-20

- **Gráfico Gauge** para monitoramento de utilização de banda em tempo real
  - Implementa 4 medidores tipo velocímetro (gauges) em grid 2x2
  - Monitora diferentes tipos de links:
    - Link Principal (Internet): 1 Gbps
    - Link Backup (MPLS): 500 Mbps
    - Link Interno (Core): 10 Gbps
    - Link VPN (Site-to-Site): 200 Mbps
  - Zonas de cor automáticas:
    - Verde (0-50%): uso normal
    - Laranja (50-80%): atenção necessária
    - Vermelho (80-100%): estado crítico
  - Indicador delta comparando com referência de 80%
  - Threshold visual em 90% (linha vermelha)
  - Valor atual exibido em Mbps e percentual
  - Número principal em destaque (40px)
  - Anotação de capacidade total abaixo de cada gauge
- Arquivo `07_gauge_bandwidth.py` (versão limpa)
- Arquivo `07_gauge_bandwidth_commented.py` (versão didática com comentários linha a linha)
- Terceiro gráfico da **Fase 2 - Gráficos Intermediários** (60% completo)

### Alterado

- README.md atualizado com link para o novo gráfico gauge
- Roadmap da Fase 2 marcado como 60% completo (3/5 tarefas)
- Estrutura do projeto atualizada com todos os arquivos atuais

### Documentação

- Comentários detalhados sobre gráficos tipo Indicator/Gauge
- Exemplos de monitoramento em tempo real
- Explicação de mode combinado (gauge+number+delta)
- Configuração de zonas coloridas (steps)
- Variações possíveis (bullet, cores dinâmicas, múltiplas zonas)
- Aplicações práticas em NOC e dashboards de monitoramento

---

## [0.4.0] - 2026-02-18

### Adicionado

- **Gráfico Heatmap** para visualização de utilização de dispositivos ao longo de 24h
  - Implementa mapa de calor com matriz 10x24 (10 dispositivos, 24 horas)
  - Escala de cores customizada (verde → laranja → vermelho)
  - Padrões realistas de utilização por horário:
    - Madrugada (00-06h): uso baixo (10-25%)
    - Horário comercial (09-18h): uso alto (50-85%)
    - Noite (21-24h): uso médio (15-35%)
  - Ajustes por tipo de dispositivo:
    - Firewalls: maior utilização (+10-20%)
    - Roteadores Core: alta utilização (+5-15%)
    - Switches de Acesso: utilização variável (+0-10%)
  - Valores exibidos em cada célula (opcional)
  - Colorbar com título e marcações a cada 20%
  - Anotações de zonas de horário (Madrugada, Comercial, Noite)
  - Estatísticas calculadas (máxima, mínima, média)
- Arquivo `06_heatmap_devices.py` (versão limpa)
- Arquivo `06_heatmap_devices_commented.py` (versão didática com comentários linha a linha)
- Segundo gráfico da **Fase 2 - Gráficos Intermediários** (40% completo)

### Alterado

- README.md atualizado com link para o novo gráfico heatmap
- Roadmap da Fase 2 marcado como 40% completo (2/5 tarefas)

### Documentação

- Comentários detalhados sobre mapas de calor
- Exemplos de padrões temporais em dispositivos de rede
- Explicação de matrizes bidimensionais e visualização de intensidade
- Variações possíveis (escalas de cores, orientação, zonas destacadas)
- Aplicações práticas em NOC e análise de capacidade

---

## [0.3.0] - 2025-10-20

### Adicionado

- **Gráfico Scatter** para análise de correlação entre latência e perda de pacotes
  - Implementa scatter plot com 50 links de rede simulados
  - Cores diferenciadas por tipo de link (Fibra, Wireless, MPLS, Internet)
  - Tamanho dinâmico dos pontos baseado em volume de tráfego (10-500 Mbps)
  - Zona visual de performance ótima (< 50ms latência, < 2% perda)
  - Características realistas por tipo de link:
    - Fibra: 5-30ms latência, 0-1% perda (melhor performance)
    - Wireless: 15-80ms latência, 0.5-5% perda (performance média)
    - MPLS: 10-50ms latência, 0-2% perda (corporativo controlado)
    - Internet: 30-150ms latência, 1-8% perda (mais variável)
- Arquivo `05_scatter_latency.py` (versão limpa)
- Arquivo `05_scatter_latency_commented.py` (versão didática com comentários linha a linha)
- Primeiro gráfico da **Fase 2 - Gráficos Intermediários**

### Alterado

- README.md atualizado com link para o novo gráfico scatter
- Roadmap da Fase 2 marcado como 20% completo (1/5 tarefas)
- Estrutura de pastas expandida para `src/intermediario/`

### Documentação

- Comentários detalhados sobre gráficos de dispersão
- Exemplos de aplicações em troubleshooting de rede
- Explicação de correlação entre métricas de rede
- Variações possíveis (linha de tendência, zonas coloridas, escala logarítmica)

---

## [0.2.0] - 2025-10-19

### Adicionado

- Dashboard MVP com 4 gráficos integrados de monitoramento de rede
  - Gráfico de linha: Tráfego de rede nas últimas 24 horas
  - Gráfico de barras agrupadas: Status de interfaces por switch (UP/DOWN)
  - Gráfico de pizza (donut): Distribuição de dispositivos por VLAN
  - Gráfico de barras horizontais: Utilização de CPU com cores dinâmicas
- Arquivo `04_dashboard_mvp.py` (versão limpa e profissional)
- Arquivo `04_dashboard_mvp_commented.py` (versão didática com comentários linha a linha)
- Guia de Versionamento Semântico em `docs/versioning_guide.md`
  - Explicação completa de MAJOR, MINOR e PATCH
  - Fluxograma de decisão de versão
  - Exemplos práticos e checklist
- Sistema de cores dinâmicas baseadas em thresholds de CPU:
  - Verde: < 50% (operação normal)
  - Laranja: 50-70% (atenção necessária)
  - Vermelho: > 70% (estado crítico)
- Posicionamento manual de gráfico de pizza usando `domain`
- Timestamp de atualização automática no rodapé do dashboard
- Estatísticas calculadas automaticamente:
  - Total de dispositivos monitorados
  - Total de interfaces (UP + DOWN)
  - Quantidade de dispositivos em estado crítico

### Alterado

- Estrutura de subplots utilizando `specs` com tipo 'xy' para todos os gráficos
- Modo de barras alterado de 'stack' (empilhadas) para 'group' (agrupadas lado a lado)
- Espaçamento horizontal aumentado de 0.12 para 0.25 para melhor visualização
- Altura do dashboard ajustada de 900px para 950px
- Método de posicionamento da pizza: de automático para manual via `domain`
- Fase 1 do roadmap marcada como 100% concluída
- README.md atualizado com link para Dashboard MVP na visualização online
- Roadmap reorganizado com status detalhado de cada fase

### Corrigido

- Erro de renderização de gráficos em branco no dashboard
- Conflito entre `add_vline()` e gráficos de pizza em subplots
- Sobreposição de textos, legendas e títulos dos gráficos
- Problema com `specs` usando tipos incompatíveis ('scatter', 'bar', 'pie')

---

## [0.1.0] - 2025-10-12

### Adicionado

- Estrutura inicial do projeto com organização profissional
- Documentação inicial completa:
  - `README.md` com descrição detalhada do projeto
  - `CHANGELOG.md` para rastreamento de mudanças
  - `docs/git_commit_guide.md` com padrões de commits profissionais
- Configuração de ambiente:
  - Arquivo `.gitignore` configurado para projetos Python
  - Arquivo `requirements.txt` com dependências (Plotly 5.18.0, Pandas 2.1.4)
  - Suporte a UTF-8 para caracteres especiais em português
- GitHub Pages configurado para visualização online
  - URL base: https://alcancil.github.io/dashboards/
  - Hospedagem a partir da pasta `/docs`

#### Gráficos Implementados

##### Gráfico 01 - Linha (Line Chart)

- Visualização de progresso semanal de labs CCNP
- Versão limpa: `01_line_chart.py`
- Versão comentada: `01_line_chart_commented.py`
- Output: `docs/01_line_chart.html`

##### Gráfico 02 - Barras (Bar Chart)

- Comparação de quantidade de labs por domínio CCNP
- Versão limpa: `02_bar_chart.py`
- Versão comentada: `02_bar_chart_commented.py`
- Output: `docs/02_bar_chart.html`

##### Gráfico 03 - Pizza/Donut (Pie Chart)

- Distribuição percentual de labs por categoria
- Versão limpa: `03_pie_chart.py`
- Versão comentada: `03_pie_chart_commented.py`
- Output: `docs/03_pie_chart.html`

### Infraestrutura

- Repositório Git inicializado com estrutura profissional
- Versionamento semântico estabelecido (SemVer)
- Documentação modular organizada em subdiretórios
- Padrão de duas versões para cada script (limpa + comentada)

---

## Convenções

### Tipos de Mudanças

- **Adicionado** - para novas funcionalidades
- **Alterado** - para mudanças em funcionalidades existentes
- **Descontinuado** - para funcionalidades que serão removidas
- **Removido** - para funcionalidades removidas
- **Corrigido** - para correções de bugs
- **Segurança** - para vulnerabilidades corrigidas  
  