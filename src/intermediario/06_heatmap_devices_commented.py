#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico Heatmap - Utilização de Dispositivos ao Longo do Tempo (VERSÃO DIDÁTICA)

Visualiza padrões de uso de CPU/Memória em dispositivos de rede durante 24h.
Esta versão contém comentários linha a linha para aprendizado.

Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-20
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import plotly.graph_objects as go              # Biblioteca para criar gráficos
import random                                  # Geração de números aleatórios

# ============================================================================
# CONFIGURAÇÃO DE REPRODUTIBILIDADE
# ============================================================================

# Seed para gerar sempre os mesmos dados aleatórios
# Útil para testes e documentação consistente
random.seed(42)

# ============================================================================
# DEFINIÇÃO DOS DISPOSITIVOS MONITORADOS
# ============================================================================

# Lista de dispositivos de rede que serão monitorados
# Hierarquia típica: Core → Distribution → Access
# Também inclui Firewalls e Load Balancers
dispositivos = [
    'RTR-CORE-01',      # Roteador Core (crítico)
    'RTR-EDGE-01',      # Roteador de Borda
    'SW-CORE-01',       # Switch Core
    'SW-DIST-01',       # Switch de Distribuição 1
    'SW-DIST-02',       # Switch de Distribuição 2
    'SW-ACCESS-01',     # Switch de Acesso 1
    'SW-ACCESS-02',     # Switch de Acesso 2
    'FW-01',            # Firewall 1 (geralmente alto uso)
    'FW-02',            # Firewall 2
    'LB-01'             # Load Balancer
]

# Total: 10 dispositivos

# ============================================================================
# DEFINIÇÃO DO PERÍODO (24 HORAS)
# ============================================================================

# Gerar lista de 24 horas no formato "HH:00"
# range(24) = 0, 1, 2, ... 23
# f'{h:02d}' = formata com 2 dígitos (01, 02, ..., 23)
horas = [f'{h:02d}:00' for h in range(24)]

# Resultado: ['00:00', '01:00', '02:00', ..., '23:00']

# ============================================================================
# GERAÇÃO DE DADOS DE UTILIZAÇÃO (MATRIZ)
# ============================================================================

# Lista que armazenará matriz de dados
# Cada linha = 1 dispositivo
# Cada coluna = 1 hora
# Formato final: matriz 10x24 (10 dispositivos, 24 horas)
utilizacao_data = []

# Iterar sobre cada dispositivo
for dispositivo in dispositivos:
    # Lista para armazenar utilização deste dispositivo ao longo das 24h
    utilizacao_hora = []
    
    # Iterar sobre cada hora do dia (0-23)
    for hora in range(24):
        # ====================================================================
        # SIMULAR PADRÕES REALISTAS POR HORÁRIO
        # ====================================================================
        
        # Madrugada (00:00 - 05:59): uso muito baixo
        if 0 <= hora < 6:
            base = random.uniform(10, 25)       # 10-25% de uso
            
        # Início da manhã (06:00 - 08:59): uso começando a subir
        elif 6 <= hora < 9:
            base = random.uniform(30, 50)       # 30-50% de uso
            
        # Manhã comercial (09:00 - 11:59): uso alto
        elif 9 <= hora < 12:
            base = random.uniform(50, 75)       # 50-75% de uso
            
        # Horário de almoço (12:00 - 13:59): uso médio
        elif 12 <= hora < 14:
            base = random.uniform(40, 60)       # 40-60% de uso
            
        # Tarde comercial (14:00 - 17:59): uso muito alto (pico)
        elif 14 <= hora < 18:
            base = random.uniform(60, 85)       # 60-85% de uso
            
        # Início da noite (18:00 - 20:59): uso diminuindo
        elif 18 <= hora < 21:
            base = random.uniform(35, 55)       # 35-55% de uso
            
        # Noite (21:00 - 23:59): uso baixo
        else:
            base = random.uniform(15, 35)       # 15-35% de uso
        
        # ====================================================================
        # AJUSTAR POR TIPO DE DISPOSITIVO
        # ====================================================================
        
        # Firewalls (FW): sempre mais carregados
        # Processam todo tráfego de entrada/saída
        if 'FW' in dispositivo:
            base += random.uniform(10, 20)      # +10-20% adicional
            
        # Roteadores Core (RTR-CORE): críticos, alto uso
        elif 'RTR-CORE' in dispositivo:
            base += random.uniform(5, 15)       # +5-15% adicional
            
        # Switches de Acesso (ACCESS): muitas portas, uso variável
        elif 'ACCESS' in dispositivo:
            base += random.uniform(0, 10)       # +0-10% adicional
        
        # Demais dispositivos: uso base sem ajuste
        
        # ====================================================================
        # GARANTIR VALORES VÁLIDOS (0-100%)
        # ====================================================================
        
        # min(100, ...) = não passa de 100%
        # max(0, ...) = não fica negativo
        utilizacao = min(100, max(0, base))
        
        # Arredondar para 1 casa decimal
        utilizacao_hora.append(round(utilizacao, 1))
    
    # Adicionar linha completa (24 valores) à matriz
    utilizacao_data.append(utilizacao_hora)

# Resultado final:
# utilizacao_data = [
#     [val1, val2, ..., val24],  ← RTR-CORE-01
#     [val1, val2, ..., val24],  ← RTR-EDGE-01
#     ...
#     [val1, val2, ..., val24]   ← LB-01
# ]

# ============================================================================
# CRIAR GRÁFICO HEATMAP
# ============================================================================

# Figure() com Heatmap
fig = go.Figure(data=go.Heatmap(
    # z = matriz de valores (altura da cor)
    z=utilizacao_data,                          # Matriz 10x24
    
    # x = eixo horizontal (horas)
    x=horas,                                    # ['00:00', '01:00', ...]
    
    # y = eixo vertical (dispositivos)
    y=dispositivos,                             # ['RTR-CORE-01', ...]
    
    # colorscale = escala de cores customizada
    # Lista de [posição, cor]
    # posição: 0.0 (mínimo) a 1.0 (máximo)
    colorscale=[
        [0.0, '#2ecc71'],                       # Verde claro (0%)
        [0.33, '#f39c12'],                      # Laranja (33%)
        [0.66, '#e74c3c'],                      # Vermelho (66%)
        [1.0, '#c0392b']                        # Vermelho escuro (100%)
    ],
    
    # colorbar = barra de legenda de cores
    colorbar=dict(
        # title = título da barra (agora como dicionário)
        title=dict(
            text='Utilização<br>(%)',            # Texto do título
                                                # <br> = quebra de linha
            side='right'                        # Posição: à direita da barra
        ),
        tickmode='linear',                      # Marcações lineares
        tick0=0,                                # Primeira marcação em 0
        dtick=20                                # Marcação a cada 20% (0, 20, 40...)
    ),
    
    # hovertemplate = tooltip customizado
    hovertemplate=(
        '<b>%{y}</b><br>' +                     # Nome do dispositivo em negrito
        'Hora: %{x}<br>' +                      # Hora
        'Utilização: %{z}%<br>' +               # Valor da utilização
        '<extra></extra>'                       # Remove informação extra
    ),
    
    # text = texto a ser exibido em cada célula
    # List comprehension aninhada: percorre cada linha e formata valores
    text=[[f'{val:.0f}%' for val in linha] for linha in utilizacao_data],
    
    # texttemplate = como exibir o texto
    texttemplate='%{text}',                     # Usa texto definido acima
    
    # textfont = fonte do texto nas células
    textfont={
        'size': 9,                              # Tamanho pequeno para caber
        'color': 'white'                        # Branco para contrastar com cores
    },
    
    showscale=True                              # Mostrar barra de cores
))

# ============================================================================
# CONFIGURAR LAYOUT DO GRÁFICO
# ============================================================================

fig.update_layout(
    title='Mapa de Calor - Utilização de Dispositivos (24h)',
                                                # Título principal
    
    # Configuração do eixo X (horas)
    xaxis=dict(
        title='Hora do Dia',                    # Título do eixo
        side='bottom',                          # Rótulos embaixo
        tickangle=0                             # Sem rotação (horizontal)
    ),
    
    # Configuração do eixo Y (dispositivos)
    yaxis=dict(
        title='Dispositivos',                   # Título do eixo
        autorange='reversed'                    # Inverter ordem (primeiro no topo)
                                                # Sem isso: último dispositivo fica no topo
    ),
    
    plot_bgcolor='white',                       # Fundo do gráfico branco
    paper_bgcolor='white',                      # Fundo da página branco
    font=dict(family='Arial', size=12),         # Fonte padrão
    height=600,                                 # Altura em pixels
    
    # margin = margens do gráfico
    margin=dict(
        l=120,                                  # Esquerda (120px para nomes longos)
        r=100,                                  # Direita (100px para colorbar)
        t=80,                                   # Topo (80px para título)
        b=80                                    # Baixo (80px para eixo X)
    )
)

# ============================================================================
# ADICIONAR ANOTAÇÕES DE ZONAS DE HORÁRIO
# ============================================================================

# Anotação 1: Madrugada
fig.add_annotation(
    x=3,                                        # Posição X (hora 03:00)
    y=-1.5,                                     # Posição Y (abaixo do gráfico)
    text='Madrugada',                           # Texto
    showarrow=False,                            # Sem seta
    font=dict(size=10, color='gray'),           # Fonte pequena e cinza
    xref='x',                                   # Referência ao eixo X
    yref='y'                                    # Referência ao eixo Y
)

# Anotação 2: Horário Comercial
fig.add_annotation(
    x=10,                                       # Posição X (hora 10:00)
    y=-1.5,                                     # Posição Y (abaixo)
    text='Horário Comercial',                   # Texto
    showarrow=False,
    font=dict(size=10, color='gray'),
    xref='x',
    yref='y'
)

# Anotação 3: Noite
fig.add_annotation(
    x=19,                                       # Posição X (hora 19:00)
    y=-1.5,                                     # Posição Y (abaixo)
    text='Noite',                               # Texto
    showarrow=False,
    font=dict(size=10, color='gray'),
    xref='x',
    yref='y'
)

# ============================================================================
# EXPORTAR PARA HTML
# ============================================================================

# Salvar como página HTML interativa
fig.write_html('../../docs/06_heatmap_devices.html')

# Mensagens de confirmação
print("✅ Heatmap salvo em: docs/06_heatmap_devices.html")
print(f"📊 Dispositivos monitorados: {len(dispositivos)}")
print(f"⏰ Período: 24 horas")

# ============================================================================
# CALCULAR E EXIBIR ESTATÍSTICAS
# ============================================================================

# Encontrar valor máximo em toda a matriz
# max(max(linha) for linha in ...) = máximo entre os máximos de cada linha
utilizacao_maxima = max(max(linha) for linha in utilizacao_data)

# Encontrar valor mínimo em toda a matriz
utilizacao_minima = min(min(linha) for linha in utilizacao_data)

# Calcular média geral
# sum(sum(linha) ...) = soma de todos os valores
# len(dispositivos) * 24 = total de células (10 * 24 = 240)
utilizacao_media = sum(sum(linha) for linha in utilizacao_data) / (len(dispositivos) * 24)

print(f"📈 Utilização máxima: {utilizacao_maxima:.1f}%")
print(f"📉 Utilização mínima: {utilizacao_minima:.1f}%")
print(f"📊 Utilização média: {utilizacao_media:.1f}%")

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Certifique-se de ter Plotly instalado:
   pip install plotly

2. Execute o script:
   python src/intermediario/06_heatmap_devices_commented.py

3. Abra o arquivo gerado:
   docs/06_heatmap_devices.html no navegador

4. Interaja com o heatmap:
   - Passe o mouse sobre células para ver detalhes
   - Use zoom (clicar e arrastar)
   - Duplo clique para resetar
   - Analise padrões visuais de cor

5. Experimente modificar:
   - Altere random.seed(42) para gerar dados diferentes
   - Mude colorscale para outras cores
   - Adicione mais dispositivos à lista
   - Altere faixas de horário (ex: apenas horário comercial)
   - Remova 'text' para heatmap sem números
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ Criar gráfico de mapa de calor (heatmap)
✅ Trabalhar com matrizes bidimensionais (linhas x colunas)
✅ Customizar escala de cores (colorscale)
✅ Adicionar texto em células do heatmap
✅ Configurar colorbar (barra de legenda)
✅ Inverter ordem do eixo Y (autorange='reversed')
✅ Adicionar anotações de contexto
✅ Simular padrões realistas por horário
✅ Ajustar valores por categoria (tipo de dispositivo)
✅ Calcular estatísticas de matriz

DIFERENÇAS DOS GRÁFICOS ANTERIORES:
- Linha: 1 variável ao longo do tempo (1D)
- Barras: categorias vs valores (1D)
- Pizza: proporções de um todo (1D)
- Scatter: correlação entre 2 variáveis (2D pontos)
- Heatmap: intensidade em 2 dimensões (2D matriz) ← NOVO

QUANDO USAR HEATMAP:
✅ Visualizar padrões temporais em múltiplos itens
✅ Identificar horários de pico
✅ Comparar comportamento entre dispositivos
✅ Análise de capacidade ao longo do tempo
✅ Detecção de anomalias visuais

APLICAÇÕES EM REDES:
- Utilização de CPU/Memória por dispositivo/hora (este exemplo)
- Tráfego por interface ao longo do tempo
- Latência por rota em diferentes horários
- Eventos de log por servidor/dia
- Disponibilidade de serviços (uptime matrix)
"""

# ============================================================================
# VARIAÇÕES POSSÍVEIS
# ============================================================================
"""
ESCALA DE CORES DIFERENTE:
colorscale='Viridis'  # Escala pronta do Plotly
# Opções: 'Viridis', 'Cividis', 'Blues', 'Reds', 'RdYlGn'

HEATMAP SEM NÚMEROS NAS CÉLULAS:
# Remover as linhas 'text' e 'texttemplate'

COLORBAR HORIZONTAL (embaixo):
colorbar=dict(
    orientation='h',
    x=0.5,
    y=-0.2
)

ADICIONAR LINHA DE SEPARAÇÃO:
# Entre dispositivos Core e Access
fig.add_hline(
    y=2.5,
    line=dict(color='black', width=2, dash='dash')
)

INVERTER EIXOS (horas no Y, dispositivos no X):
# Trocar x e y nos parâmetros do Heatmap
x=dispositivos,
y=horas,

DESTACAR VALORES EXTREMOS:
# Células com utilização > 80%
for i, dispositivo in enumerate(dispositivos):
    for j, hora in enumerate(horas):
        if utilizacao_data[i][j] > 80:
            fig.add_annotation(
                x=j, y=i,
                text='⚠️',
                showarrow=False,
                font=dict(size=16)
            )

ADICIONAR DIAS DA SEMANA (7x24):
dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
# Gerar matriz 7x24 ao invés de 10x24
"""