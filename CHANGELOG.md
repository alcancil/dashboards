## Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Em Desenvolvimento

- Integração com dados reais via SNMP/SSH
- Filtros dropdown interativos
- Dashboard de progresso CCNP ENCOR por domínio

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
  