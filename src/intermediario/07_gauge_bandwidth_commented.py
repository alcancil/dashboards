#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico Gauge - Medidor de Banda de Links (VERSÃO DIDÁTICA)

Visualiza utilização atual de banda em diferentes links de rede.
Esta versão contém comentários linha a linha para aprendizado.

Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-20
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import plotly.graph_objects as go              # Biblioteca para criar gráficos
from plotly.subplots import make_subplots      # Função para múltiplos gráficos
import random                                  # Geração de números aleatórios

# ============================================================================
# CONFIGURAÇÃO DE REPRODUTIBILIDADE
# ============================================================================

# Seed para gerar sempre os mesmos dados aleatórios
random.seed(42)

# ============================================================================
# DEFINIÇÃO DOS LINKS DE REDE
# ============================================================================

# Lista de links com suas características
# Cada link tem: nome, tipo, capacidade total, utilização atual
links = [
    {
        'nome': 'Link Principal',               # Link principal da empresa
        'tipo': 'Internet',                     # Tipo de conexão
        'capacidade': 1000,                     # Capacidade: 1 Gbps = 1000 Mbps
        'utilizado': random.randint(500, 850)   # Uso atual: entre 500-850 Mbps
    },
    {
        'nome': 'Link Backup',                  # Link de backup/redundância
        'tipo': 'MPLS',                         # Multi-Protocol Label Switching
        'capacidade': 500,                      # Capacidade: 500 Mbps
        'utilizado': random.randint(100, 300)   # Uso atual: entre 100-300 Mbps
    },
    {
        'nome': 'Link Interno',                 # Link entre datacenters
        'tipo': 'Core',                         # Rede interna (core)
        'capacidade': 10000,                    # Capacidade: 10 Gbps = 10000 Mbps
        'utilizado': random.randint(3000, 7000) # Uso atual: entre 3-7 Gbps
    },
    {
        'nome': 'Link VPN',                     # VPN site-to-site
        'tipo': 'Site-to-Site',                 # Conecta filiais
        'capacidade': 200,                      # Capacidade: 200 Mbps
        'utilizado': random.randint(50, 180)    # Uso atual: entre 50-180 Mbps
    }
]

# ============================================================================
# CALCULAR PERCENTUAIS DE UTILIZAÇÃO
# ============================================================================

# Adicionar campo 'percentual' a cada link
# Fórmula: (utilizado / capacidade) * 100
for link in links:
    link['percentual'] = round((link['utilizado'] / link['capacidade']) * 100, 1)
    # round(..., 1) = arredonda para 1 casa decimal

# Exemplo de resultado:
# Se utilizado=650 e capacidade=1000:
# percentual = (650/1000)*100 = 65.0%

# ============================================================================
# CRIAR ESTRUTURA DE SUBPLOTS (2x2)
# ============================================================================

# make_subplots cria grade de gráficos
fig = make_subplots(
    rows=2,                                     # 2 linhas
    cols=2,                                     # 2 colunas
    
    # specs define o tipo de cada posição
    specs=[
        [{'type': 'indicator'}, {'type': 'indicator'}],  # Linha 1: 2 indicadores
        [{'type': 'indicator'}, {'type': 'indicator'}]   # Linha 2: 2 indicadores
    ],
    # 'indicator' = tipo especial para gauges, números, deltas
    
    # Títulos de cada gauge
    # List comprehension cria título formatado para cada link
    # <sub> = subtítulo em HTML (texto menor)
    subplot_titles=[f"{link['nome']}<br><sub>{link['tipo']}</sub>" for link in links],
    
    vertical_spacing=0.25,                      # Espaço vertical entre linhas (25%)
    horizontal_spacing=0.15                     # Espaço horizontal entre colunas (15%)
)

# ============================================================================
# DEFINIR POSIÇÕES DOS GAUGES NO GRID
# ============================================================================

# Lista de posições (row, col) para cada gauge
# Gauge 1: linha 1, coluna 1 (superior esquerdo)
# Gauge 2: linha 1, coluna 2 (superior direito)
# Gauge 3: linha 2, coluna 1 (inferior esquerdo)
# Gauge 4: linha 2, coluna 2 (inferior direito)
positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

# ============================================================================
# ADICIONAR GAUGES AO GRÁFICO
# ============================================================================

# zip() combina duas listas em pares: (link, posição)
# enumerate() adiciona índice: 0, 1, 2, 3
for idx, (link, pos) in enumerate(zip(links, positions)):
    
    # add_trace() adiciona um elemento ao gráfico
    fig.add_trace(
        go.Indicator(                           # Indicator = tipo para gauges/números
            mode='gauge+number+delta',          # Modos combinados:
                                                # gauge = mostrar velocímetro
                                                # number = mostrar número grande
                                                # delta = mostrar diferença de referência
            
            value=link['percentual'],           # Valor principal (percentual de uso)
            
            domain={'x': [0, 1], 'y': [0, 1]},  # Área ocupada pelo gauge (100%)
            
            # Título do gauge (abaixo do número principal)
            title={
                'text': f"{link['utilizado']} Mbps",  # Texto: "650 Mbps"
                'font': {'size': 14}            # Tamanho da fonte
            },
            
            # Delta = comparação com valor de referência
            delta={
                'reference': 80,                # Referência: 80% (threshold)
                                                # Se valor > 80: mostra diferença em vermelho
                                                # Se valor < 80: mostra diferença em verde
                'increasing': {'color': 'red'}, # Cor se aumentando (ruim)
                'decreasing': {'color': 'green'} # Cor se diminuindo (bom)
            },
            
            # Número principal (grande no centro)
            number={
                'suffix': '%',                  # Sufixo: adiciona "%" após o número
                'font': {'size': 40}            # Tamanho: número bem grande
            },
            
            # Configuração do gauge (velocímetro)
            gauge={
                # Eixo do gauge
                'axis': {
                    'range': [0, 100],          # Escala: 0% a 100%
                    'tickwidth': 1,             # Espessura das marcações
                    'tickcolor': 'darkgray'     # Cor das marcações
                },
                
                'bar': {'color': 'darkblue'},   # Cor do ponteiro/barra
                
                'bgcolor': 'white',             # Cor de fundo do gauge
                
                'borderwidth': 2,               # Espessura da borda
                'bordercolor': 'gray',          # Cor da borda
                
                # Zonas coloridas (steps)
                # Define faixas com cores diferentes
                'steps': [
                    {'range': [0, 50], 'color': '#2ecc71'},    # 0-50%: Verde (OK)
                    {'range': [50, 80], 'color': '#f39c12'},   # 50-80%: Laranja (Atenção)
                    {'range': [80, 100], 'color': '#e74c3c'}   # 80-100%: Vermelho (Crítico)
                ],
                
                # Linha de threshold (limite crítico)
                'threshold': {
                    'line': {
                        'color': 'red',         # Cor da linha
                        'width': 4              # Espessura da linha
                    },
                    'thickness': 0.75,          # Espessura relativa
                    'value': 90                 # Posição: 90%
                }
            }
        ),
        row=pos[0],                             # Linha da posição
        col=pos[1]                              # Coluna da posição
    )
    
    # ========================================================================
    # ADICIONAR ANOTAÇÃO DE CAPACIDADE
    # ========================================================================
    
    # add_annotation() adiciona texto em posição específica
    fig.add_annotation(
        text=f'Capacidade: {link["capacidade"]} Mbps',  # Texto
        
        # Referência aos eixos (necessário para posicionamento correto)
        # Primeiro gauge: 'x', 'y'
        # Demais gauges: 'x2', 'y2', 'x3', 'y3', 'x4', 'y4'
        xref=f'x{idx+1}' if idx > 0 else 'x',
        yref=f'y{idx+1}' if idx > 0 else 'y',
        
        x=0.5,                                  # Posição X: centro (50%)
        y=-0.3,                                 # Posição Y: abaixo do gauge
        
        showarrow=False,                        # Não mostrar seta
        
        font=dict(size=11, color='gray')        # Fonte pequena e cinza
    )

# ============================================================================
# CONFIGURAR LAYOUT GERAL
# ============================================================================

fig.update_layout(
    title={
        'text': '📊 Monitoramento de Banda - Links de Rede',
        'x': 0.5,                               # Centralizar título
        'xanchor': 'center',
        'font': {'size': 24}
    },
    height=800,                                 # Altura total: 800 pixels
    showlegend=False,                           # Não mostrar legenda (não aplicável)
    paper_bgcolor='white',                      # Fundo branco
    font=dict(family='Arial', size=12)          # Fonte padrão
)

# ============================================================================
# EXPORTAR PARA HTML
# ============================================================================

# Salvar como página HTML interativa
fig.write_html('../../docs/07_gauge_bandwidth.html')

# Mensagem de confirmação
print("✅ Gauge salvo em: docs/07_gauge_bandwidth.html")

# ============================================================================
# EXIBIR STATUS DOS LINKS NO TERMINAL
# ============================================================================

print(f"\n📊 Status dos Links:")

# Iterar sobre cada link e exibir informações
for link in links:
    # Definir emoji baseado no percentual
    # 🟢 Verde: < 50% (OK)
    # 🟡 Amarelo: 50-80% (Atenção)
    # 🔴 Vermelho: > 80% (Crítico)
    if link['percentual'] < 50:
        status = '🟢'
    elif link['percentual'] < 80:
        status = '🟡'
    else:
        status = '🔴'
    
    # Exibir linha formatada
    print(f"{status} {link['nome']}: {link['utilizado']}/{link['capacidade']} Mbps ({link['percentual']}%)")

# Exemplo de saída:
# 🟢 Link Principal: 650/1000 Mbps (65.0%)
# 🟢 Link Backup: 180/500 Mbps (36.0%)
# 🟡 Link Interno: 5200/10000 Mbps (52.0%)
# 🔴 Link VPN: 165/200 Mbps (82.5%)

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Certifique-se de ter Plotly instalado:
   pip install plotly

2. Execute o script:
   python src/intermediario/07_gauge_bandwidth_commented.py

3. Abra o arquivo gerado:
   docs/07_gauge_bandwidth.html no navegador

4. Interaja com os gauges:
   - Visualize os 4 links simultaneamente
   - Compare percentuais de utilização
   - Identifique links críticos (vermelho)
   - Passe o mouse para ver detalhes

5. Experimente modificar:
   - Altere random.seed(42) para novos dados
   - Mude cores das zonas (steps)
   - Ajuste threshold de 90% para outro valor
   - Adicione mais links à lista
   - Mude capacidades e utilizações
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ Criar gráfico tipo Indicator/Gauge (velocímetro)
✅ Usar mode combinado (gauge+number+delta)
✅ Definir zonas coloridas (steps)
✅ Adicionar threshold visual (linha de limite)
✅ Calcular percentuais de utilização
✅ Usar delta para comparação com referência
✅ Combinar múltiplos gauges em grid 2x2
✅ Adicionar anotações em posições específicas
✅ Referenciar eixos em subplots (x, x2, x3, x4)
✅ Formatar números com sufixos (%)

DIFERENÇAS DOS GRÁFICOS ANTERIORES:
- Linha/Barras/Pizza: mostram dados históricos
- Scatter: correlação entre variáveis
- Heatmap: matriz de intensidades
- Gauge: valor atual vs referência (tempo real) ← NOVO

QUANDO USAR GAUGE:
✅ Monitoramento em tempo real
✅ Mostrar valor atual vs capacidade
✅ Dashboards de NOC (Network Operations Center)
✅ KPIs com metas definidas
✅ Alertas visuais rápidos (verde/amarelo/vermelho)

APLICAÇÕES EM REDES:
- Utilização de banda (este exemplo)
- CPU/Memória de dispositivos
- Latência atual vs SLA
- Uptime vs meta
- Taxa de pacotes por segundo
- Throughput de interfaces
"""

# ============================================================================
# VARIAÇÕES POSSÍVEIS
# ============================================================================
"""
GAUGE SIMPLES (SEM ZONAS):
gauge={
    'axis': {'range': [0, 100]},
    'bar': {'color': 'blue'}
}

APENAS NÚMERO (SEM GAUGE):
mode='number+delta'

GAUGE BULLET (ESTILO LINEAR):
go.Indicator(
    mode='gauge+number',
    gauge={'shape': 'bullet', ...}
)

CORES DINÂMICAS BASEADAS NO VALOR:
bar_color = 'green' if link['percentual'] < 50 else 'orange' if link['percentual'] < 80 else 'red'
gauge={'bar': {'color': bar_color}}

ADICIONAR MAIS ZONAS:
'steps': [
    {'range': [0, 25], 'color': '#27ae60'},   # Verde escuro
    {'range': [25, 50], 'color': '#2ecc71'},  # Verde claro
    {'range': [50, 75], 'color': '#f39c12'},  # Laranja
    {'range': [75, 90], 'color': '#e67e22'},  # Laranja escuro
    {'range': [90, 100], 'color': '#e74c3c'}  # Vermelho
]

REFERÊNCIA CUSTOMIZADA POR LINK:
delta={'reference': link['capacidade'] * 0.8}  # 80% da capacidade
"""