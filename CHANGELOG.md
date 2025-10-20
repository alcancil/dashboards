# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Em Desenvolvimento

- Gráfico scatter para análise de latência vs perda de pacotes
- Heatmap de utilização de dispositivos ao longo do tempo
- Gauge de medidor de banda (velocímetro)
- Timeline de janelas de manutenção
- Integração com dados reais via SNMP/SSH
- Filtros dropdown interativos
- Dashboard de progresso CCNP ENCOR por domínio

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

### Corrigido

- Erro de renderização de gráficos em branco no dashboard
- Conflito entre `add_vline()` e gráficos de pizza em subplots
- Sobreposição de textos, legendas e títulos dos gráficos
- Problema com `specs` usando tipos incompatíveis ('scatter', 'bar', 'pie')

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

## Convenções

### Tipos de Mudanças

- **Adicionado** - para novas funcionalidades
- **Alterado** - para mudanças em funcionalidades existentes
- **Descontinuado** - para funcionalidades que serão removidas
- **Removido** - para funcionalidades removidas
- **Corrigido** - para correções de bugs
- **Segurança** - para vulnerabilidades corrigidas  
