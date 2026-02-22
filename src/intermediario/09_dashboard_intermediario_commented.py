#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Intermediário - Monitoramento Completo com Filtros (VERSÃO DIDÁTICA)

Integra 4 gráficos intermediários com controles interativos.
Esta versão contém comentários linha a linha para aprendizado.

Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-20
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import plotly.graph_objects as go             # Objetos gráficos individuais (Scatter, Heatmap, etc.)
from plotly.subplots import make_subplots     # Criar grade de múltiplos subgráficos
import random                                 # Números aleatórios para dados simulados
from datetime import datetime, timedelta      # Manipulação de datas

# IMPORTANTE: Neste script usamos graph_objects (go) ao invés de figure_factory (ff)
# porque precisamos combinar diferentes tipos de gráfico em um único dashboard.
# figure_factory cria figuras prontas, mas sem flexibilidade para subplots mistos.

# ============================================================================
# CONFIGURAÇÃO DE REPRODUTIBILIDADE
# ============================================================================

# Seed garante que random.choice/randint gerem os mesmos valores em toda execução
random.seed(42)

# ============================================================================
# DADOS - SCATTER (LATÊNCIA vs PERDA DE PACOTES)
# ============================================================================

# Tipos de link disponíveis na infraestrutura
tipos_link = ['Fibra', 'Wireless', 'MPLS', 'Internet']

# Paleta de cores para cada tipo de link (usada no scatter plot)
cores_tipos = {
    'Fibra': '#00CC96',     # Verde-água (mais estável/confiável)
    'Wireless': '#FFA15A',  # Laranja (variável)
    'MPLS': '#636EFA',      # Azul (corporativo/dedicado)
    'Internet': '#EF553B'   # Vermelho (menos confiável)
}

# Lista que armazenará os 50 links simulados
links_scatter = []

# Gerar 50 links com características realistas por tipo
for i in range(50):
    # Escolher tipo de link aleatoriamente
    tipo = random.choice(tipos_link)
    
    # ========================================================================
    # Definir latência e perda de pacotes baseado no tipo de link
    # Cada tipo tem faixa realista de valores:
    # ========================================================================
    
    if tipo == 'Fibra':
        latencia = random.uniform(5, 30)        # Fibra: baixa latência (5-30ms)
        perda = random.uniform(0, 1)            # Fibra: perda mínima (0-1%)
    elif tipo == 'Wireless':
        latencia = random.uniform(15, 80)       # Wireless: latência variável (15-80ms)
        perda = random.uniform(0.5, 5)          # Wireless: perda moderada (0.5-5%)
    elif tipo == 'MPLS':
        latencia = random.uniform(10, 50)       # MPLS: latência controlada (10-50ms)
        perda = random.uniform(0, 2)            # MPLS: perda baixa (0-2%)
    else:                                       # Internet
        latencia = random.uniform(30, 150)      # Internet: latência alta (30-150ms)
        perda = random.uniform(1, 8)            # Internet: perda maior (1-8%)
    
    # Armazenar dados do link com valores arredondados
    links_scatter.append({
        'tipo': tipo,
        'latencia': round(latencia, 2),         # 2 casas decimais para ms
        'perda': round(perda, 2)                # 2 casas decimais para %
    })

# Resultado: lista com 50 dicts, cada um com tipo/latencia/perda

# ============================================================================
# DADOS - HEATMAP (UTILIZAÇÃO POR DISPOSITIVO E HORA)
# ============================================================================

# Dispositivos monitorados (eixo Y do heatmap)
dispositivos = ['RTR-CORE-01', 'RTR-EDGE-01', 'SW-CORE-01', 'SW-DIST-01', 
                'FW-01', 'LB-01']

# Horas do dia formatadas como '00:00', '01:00', ..., '23:00' (eixo X)
# f'{h:02d}:00' → formata com zero à esquerda: 0→'00:00', 9→'09:00'
horas = [f'{h:02d}:00' for h in range(24)]

# Matriz de utilização: lista de listas
# Estrutura: utilizacao_data[dispositivo][hora] = percentual (0-100)
utilizacao_data = []

for dispositivo in dispositivos:
    # Lista de utilização por hora para este dispositivo
    utilizacao_hora = []
    
    for hora in range(24):
        # ====================================================================
        # Simular padrão realista de uso ao longo do dia:
        # Madrugada → Ramp-up → Horário comercial → Noite
        # ====================================================================
        
        if 0 <= hora < 6:
            base = random.uniform(10, 25)       # Madrugada: tráfego baixo (backups, etc.)
        elif 6 <= hora < 9:
            base = random.uniform(30, 50)       # Ramp-up: usuários chegando
        elif 9 <= hora < 18:
            base = random.uniform(50, 85)       # Horário comercial: pico de utilização
        else:
            base = random.uniform(15, 35)       # Noite: tráfego reduzido
        
        # Firewall tem carga extra por inspeção de pacotes (stateful inspection)
        # Isso é realista: FW processa todo tráfego, logo usa mais CPU/memória
        if 'FW' in dispositivo:
            base += random.uniform(10, 20)      # +10-20% por overhead de inspeção
        
        # Garantir que o valor fique entre 0 e 100%
        # min(100, max(0, base)) = clamp entre 0 e 100
        utilizacao_hora.append(round(min(100, max(0, base)), 1))
    
    # Adicionar lista de 24 valores para este dispositivo
    utilizacao_data.append(utilizacao_hora)

# Resultado: matriz 6x24 (6 dispositivos × 24 horas)

# ============================================================================
# DADOS - GAUGE (UTILIZAÇÃO DE BANDA DOS LINKS PRINCIPAIS)
# ============================================================================

# Dicionário com dados reais (simulados) de capacidade e uso atual
links_gauge = [
    {'nome': 'Link Principal', 'capacidade': 1000,  'utilizado': 650},   # 1 Gbps, 65% uso
    {'nome': 'Link Backup',    'capacidade': 500,   'utilizado': 180},   # 500 Mbps, 36% uso
    {'nome': 'Link Core',      'capacidade': 10000, 'utilizado': 5200},  # 10 Gbps, 52% uso
    {'nome': 'Link VPN',       'capacidade': 200,   'utilizado': 165}    # 200 Mbps, 82.5% uso
]

# Calcular percentual de utilização para cada link
# Itera por referência: modifica o dicionário original (não cria cópia)
for link in links_gauge:
    link['percentual'] = round((link['utilizado'] / link['capacidade']) * 100, 1)

# Resultado: cada link agora tem chave 'percentual' calculada

# ============================================================================
# CRIAR DASHBOARD 2x2 COM SUBPLOTS DE TIPOS DIFERENTES
# ============================================================================

# make_subplots() cria grade de subgráficos
# Diferente de charts simples: cada célula pode ter tipo diferente
fig = make_subplots(
    rows=2, cols=2,                             # Grade 2 linhas × 2 colunas = 4 gráficos
    
    # Títulos de cada subplot (ordem: esquerda→direita, cima→baixo)
    subplot_titles=(
        '📊 Latência vs Perda de Pacotes',      # [row=1, col=1]
        '🔥 Utilização de Dispositivos (24h)',   # [row=1, col=2]
        '📡 Utilização de Banda',               # [row=2, col=1]
        '📋 Resumo de Status'                   # [row=2, col=2]
    ),
    
    # CRÍTICO: specs define o tipo de cada célula
    # Sem isso, Plotly não sabe como renderizar tipos especiais (indicator, table)
    specs=[
        [{'type': 'scatter'},    {'type': 'heatmap'}],   # Linha 1: scatter + heatmap
        [{'type': 'indicator'}, {'type': 'table'}]        # Linha 2: gauge + tabela
    ],
    
    vertical_spacing=0.15,                      # 15% de espaço vertical entre linhas
    horizontal_spacing=0.12                     # 12% de espaço horizontal entre colunas
)

# ============================================================================
# GRÁFICO 1 (row=1, col=1): SCATTER - LATÊNCIA vs PERDA DE PACOTES
# ============================================================================

# Criar uma série (trace) por tipo de link para ter legenda separada por cor
for tipo in tipos_link:
    # Filtrar apenas os links deste tipo
    links_tipo = [l for l in links_scatter if l['tipo'] == tipo]
    
    # Adicionar série de pontos para este tipo
    fig.add_trace(
        go.Scatter(
            x=[l['latencia'] for l in links_tipo],     # Eixo X = latência (ms)
            y=[l['perda'] for l in links_tipo],         # Eixo Y = perda de pacotes (%)
            mode='markers',                             # Apenas pontos (sem linha)
            name=tipo,                                  # Nome na legenda
            marker=dict(
                size=8,                                 # Tamanho dos pontos
                color=cores_tipos[tipo],                # Cor do tipo (do dicionário)
                opacity=0.7                             # 70% opaco (sobreposição visível)
            ),
            # Template do tooltip ao passar mouse
            # %{x} = valor do eixo X, %{y} = valor do eixo Y
            hovertemplate=f'<b>{tipo}</b><br>Latência: %{{x}}ms<br>Perda: %{{y}}%<extra></extra>'
        ),
        row=1, col=1                                    # Posicionar no subplot [1,1]
    )

# Configurar rótulos dos eixos do subplot [1,1]
fig.update_xaxes(title_text="Latência (ms)", row=1, col=1)
fig.update_yaxes(title_text="Perda (%)", row=1, col=1)

# ============================================================================
# GRÁFICO 2 (row=1, col=2): HEATMAP - UTILIZAÇÃO POR HORA
# ============================================================================

fig.add_trace(
    go.Heatmap(
        z=utilizacao_data,                              # Matriz 6x24 com valores 0-100
        x=horas,                                        # Eixo X = horas (00:00 a 23:00)
        y=dispositivos,                                 # Eixo Y = dispositivos
        
        # Escala de cor: verde (baixo) → laranja (médio) → vermelho (alto)
        # Formato: lista de [posição_0_a_1, 'cor']
        colorscale=[
            [0,   '#2ecc71'],   # 0% utilização → verde
            [0.5, '#f39c12'],   # 50% utilização → laranja
            [1,   '#e74c3c']    # 100% utilização → vermelho
        ],
        
        showscale=False,                                # Ocultar barra de escala (economiza espaço)
        
        # Tooltip: nome do dispositivo, hora e percentual de utilização
        hovertemplate='<b>%{y}</b><br>Hora: %{x}<br>Utilização: %{z}%<extra></extra>'
    ),
    row=1, col=2                                        # Posicionar no subplot [1,2]
)

# Configurar rótulos dos eixos do subplot [1,2]
fig.update_xaxes(title_text="Hora", row=1, col=2)
fig.update_yaxes(title_text="Dispositivos", row=1, col=2)

# ============================================================================
# GRÁFICO 3 (row=2, col=1): GAUGE - UTILIZAÇÃO MÉDIA DE BANDA
# ============================================================================

# Calcular média de utilização de todos os links
media_utilizacao = sum(l['percentual'] for l in links_gauge) / len(links_gauge)

fig.add_trace(
    go.Indicator(
        mode='gauge+number',                            # Exibir gauge + número central
        value=round(media_utilizacao, 1),               # Valor atual (média calculada)
        title={'text': 'Utilização Média de Banda'},    # Título acima do gauge
        
        # Configuração do número exibido no centro
        number={
            'suffix': '%',                              # Adicionar "%" após o número
            'font': {'size': 40}                        # Fonte grande para destaque
        },
        
        # Configuração do gauge (medidor semicircular)
        gauge={
            'axis': {'range': [0, 100]},                # Escala de 0 a 100%
            
            # Cor da barra de progresso (ponteiro)
            'bar': {'color': 'darkblue'},
            
            # Zonas coloridas de fundo (semáforo)
            'steps': [
                {'range': [0, 50],   'color': '#2ecc71'},   # Verde: normal (0-50%)
                {'range': [50, 80],  'color': '#f39c12'},   # Amarelo: atenção (50-80%)
                {'range': [80, 100], 'color': '#e74c3c'}    # Vermelho: crítico (80-100%)
            ],
            
            # Linha threshold: limite máximo aceitável (90%)
            'threshold': {
                'line': {'color': 'red', 'width': 4},   # Linha vermelha grossa
                'thickness': 0.75,                       # 75% da altura do gauge
                'value': 90                              # Threshold em 90%
            }
        }
    ),
    row=2, col=1                                        # Posicionar no subplot [2,1]
)

# ============================================================================
# GRÁFICO 4 (row=2, col=2): TABELA - RESUMO DE STATUS DOS LINKS
# ============================================================================

fig.add_trace(
    go.Table(
        # Configuração do cabeçalho
        header=dict(
            # Colunas com texto em negrito (HTML dentro das strings)
            values=['<b>Link</b>', '<b>Capacidade</b>', '<b>Usado</b>', '<b>Status</b>'],
            fill_color='#3498db',                       # Azul no cabeçalho
            font=dict(color='white', size=12),          # Texto branco
            align='left'                                # Alinhamento à esquerda
        ),
        
        # Configuração das células de dados
        cells=dict(
            values=[
                # Coluna 1: Nome do link
                [l['nome'] for l in links_gauge],
                
                # Coluna 2: Capacidade formatada em Mbps
                [f"{l['capacidade']} Mbps" for l in links_gauge],
                
                # Coluna 3: Utilização com valor absoluto e percentual
                [f"{l['utilizado']} Mbps ({l['percentual']}%)" for l in links_gauge],
                
                # Coluna 4: Semáforo de status com emoji
                # 🟢 < 50% | 🟡 50-80% | 🔴 > 80%
                ['🟢' if l['percentual'] < 50 else '🟡' if l['percentual'] < 80 else '🔴' 
                 for l in links_gauge]
            ],
            
            # Alternância de cores nas linhas (zebra striping)
            # ['#ecf0f1', 'white'] * 2 = ['#ecf0f1', 'white', '#ecf0f1', 'white']
            fill_color=[['#ecf0f1', 'white'] * 2],
            
            align='left',
            font=dict(size=11)
        )
    ),
    row=2, col=2                                        # Posicionar no subplot [2,2]
)

# ============================================================================
# LAYOUT GLOBAL DO DASHBOARD
# ============================================================================

# update_layout() aplica configurações globais ao fig inteiro
fig.update_layout(
    # Título principal do dashboard
    title={
        'text': (
            '📊 Dashboard Intermediário - Monitoramento de Rede<br>' +
            # Subtítulo dinâmico com data/hora atual
            # strftime() formata datetime: %d=dia, %m=mês, %Y=ano, %H=hora, %M=min, %S=seg
            f'<sub>Atualizado: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</sub>'
        ),
        'x': 0.5,                                       # Centralizar horizontalmente
        'xanchor': 'center',                            # Âncora no centro
        'font': {'size': 24}                            # Tamanho da fonte do título
    },
    
    height=900,                                         # Altura total do dashboard em pixels
    showlegend=True,                                    # Exibir legenda (para o scatter)
    
    # Posicionar legenda no topo direito, horizontal
    legend=dict(
        orientation='h',                                # Horizontal (lado a lado)
        yanchor='bottom',                               # Ancoragem vertical embaixo
        y=1.02,                                         # Posição Y: ligeiramente acima do gráfico
        xanchor='right',                                # Ancoragem horizontal à direita
        x=1                                             # Posição X: extrema direita
    ),
    
    plot_bgcolor='#F8F9FA',                             # Fundo dos gráficos (cinza claro)
    paper_bgcolor='white',                              # Fundo da página (branco)
    font=dict(family='Arial', size=12)                  # Fonte padrão de todo o dashboard
)

# ============================================================================
# EXPORTAR PARA HTML
# ============================================================================

# Salvar dashboard completo como arquivo HTML interativo
fig.write_html('../../docs/09_dashboard_intermediario.html')

# Mensagem de confirmação no terminal
print("✅ Dashboard salvo em: docs/09_dashboard_intermediario.html")

# ============================================================================
# EXIBIR ESTATÍSTICAS NO TERMINAL
# ============================================================================

print(f"\n📊 Resumo do Dashboard:")
print(f"  📈 Links analisados: {len(links_scatter)}")
print(f"  🖥️  Dispositivos monitorados: {len(dispositivos)}")
print(f"  📡 Links de banda: {len(links_gauge)}")
print(f"  📊 Utilização média: {media_utilizacao:.1f}%")

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Certifique-se de ter Plotly instalado:
   pip install plotly

2. Execute o script:
   python src/intermediario/09_dashboard_intermediario_commented.py

3. Abra o arquivo gerado:
   docs/09_dashboard_intermediario.html no navegador

4. Interaja com o dashboard:
   - Passe o mouse sobre pontos do scatter para ver latência/perda por tipo
   - Passe o mouse sobre células do heatmap para ver utilização exata por hora
   - Observe o gauge indicando a média de utilização de banda
   - Leia a tabela para ver o status resumido de cada link

5. Experimente modificar:
   - Altere random.seed(42) para gerar novos cenários
   - Adicione mais dispositivos à lista 'dispositivos'
   - Mude os valores de capacidade/utilizado em links_gauge
   - Ajuste os thresholds do gauge (50%, 80%, 90%)
   - Adicione um 5º subplot convertendo para grade 3x2
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ Criar dashboard com múltiplos tipos de gráfico (subplots mistos)
✅ Usar make_subplots() com specs para tipos heterogêneos
✅ Adicionar traces com row/col para posicionamento preciso
✅ Combinar Scatter, Heatmap, Indicator (Gauge) e Table em uma figura
✅ Configurar colorscale personalizada no Heatmap
✅ Criar tabela com zebra striping e emojis de status
✅ Posicionar legenda global fora dos gráficos
✅ Usar datetime.now().strftime() para timestamp dinâmico
✅ Calcular percentuais e aplicar lógica de semáforo

DIFERENÇA ENTRE FIGURE_FACTORY E GRAPH_OBJECTS:
- figure_factory (ff): funções prontas para gráficos específicos (Gantt, Distplot, etc.)
  → Mais simples, menos flexível
- graph_objects (go): blocos de construção primitivos
  → Mais verboso, mas suporta qualquer combinação de tipos

SPECS DISPONÍVEIS EM MAKE_SUBPLOTS:
- 'scatter'   → Scatter, Bar, Box, Violin, Histogram...
- 'heatmap'   → Heatmap, Contour
- 'indicator' → Gauge, Number, Delta (go.Indicator)
- 'table'     → Tabela de dados (go.Table)
- 'pie'       → Pizza, Donut (go.Pie)
- 'scene'     → Gráficos 3D (go.Scatter3d, go.Surface)

QUANDO USAR DASHBOARD MULTI-GRÁFICO:
✅ Visão consolidada de métricas relacionadas
✅ NOC/SOC (Network/Security Operations Center)
✅ Relatórios executivos
✅ Monitoramento em tempo real (com atualização automática)
✅ Correlação visual entre diferentes fontes de dados

APLICAÇÕES EM REDES:
- NOC dashboard com latência, utilização e alarmes
- Relatório de SLA com disponibilidade e performance
- Análise de capacidade: uso atual vs capacidade instalada
- Health check de infraestrutura crítica
- Comparativo de QoS por tipo de tráfego
"""

# ============================================================================
# VARIAÇÕES POSSÍVEIS
# ============================================================================
"""
ADICIONAR 5º GRÁFICO (LINHA DO TEMPO):
fig = make_subplots(
    rows=3, cols=2,
    specs=[
        [{'type': 'scatter'}, {'type': 'heatmap'}],
        [{'type': 'indicator'}, {'type': 'table'}],
        [{'colspan': 2, 'type': 'scatter'}, None]  # Span de 2 colunas
    ]
)

ATUALIZAÇÃO AUTOMÁTICA (SIMULAÇÃO REAL-TIME):
# Com Dash (framework web da Plotly):
# from dash import Dash, dcc, html
# from dash.dependencies import Input, Output
# app.callback(...)(update_dashboard)

COLORBAR NO HEATMAP:
# Remover showscale=False e adicionar:
go.Heatmap(
    ...
    colorbar=dict(title='Utilização %', x=1.02)
)

TABELA COM LINKS CLICÁVEIS:
# Usar HTML nas células:
values=['<a href="http://...">Link Principal</a>', ...]

GAUGE POR LINK (4 GAUGES):
# Criar make_subplots com 4 células do tipo 'indicator'
# e adicionar um go.Indicator para cada link em links_gauge
"""