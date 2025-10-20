#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard MVP - Monitoramento de Rede (VERSÃO DIDÁTICA)

Dashboard básico com 4 gráficos para monitoramento de infraestrutura.
Esta versão contém comentários linha a linha para aprendizado.

Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-19
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import plotly.graph_objects as go              # Biblioteca para criar gráficos
from plotly.subplots import make_subplots      # Função para criar múltiplos gráficos
from datetime import datetime, timedelta       # Manipulação de datas/horas

# ============================================================================
# DADOS DO GRÁFICO 1 - TRÁFEGO DE REDE (24 HORAS)
# ============================================================================

# Gerar últimas 24 horas no formato HH:MM
# range(23, -1, -1) = 23, 22, 21... até 0 (24 valores)
# datetime.now() = hora atual
# timedelta(hours=i) = subtrai 'i' horas
# strftime('%H:%M') = formata como "14:30"
horas = [(datetime.now() - timedelta(hours=i)).strftime('%H:%M') for i in range(23, -1, -1)]

# Tráfego em Mbps para cada hora
# Valores simulados representando um dia típico:
# - Menor tráfego: madrugada (120-150 Mbps)
# - Pico: horário comercial (220-240 Mbps)
# - Redução: final do dia
trafego_mbps = [120, 135, 145, 150, 160, 155, 170, 180, 190, 185,
                200, 210, 220, 230, 240, 235, 225, 215, 205, 195,
                180, 170, 150, 140]

# ============================================================================
# DADOS DO GRÁFICO 2 - STATUS DE INTERFACES POR SWITCH
# ============================================================================

# Lista de switches da infraestrutura
# Hierarquia: CORE → DISTRIBUIÇÃO → ACESSO
switches = ['SW-CORE-01', 'SW-DIST-01', 'SW-DIST-02', 'SW-ACCESS-01', 'SW-ACCESS-02']

# Quantidade de interfaces UP (operacionais) em cada switch
interfaces_up = [22, 18, 20, 45, 42]

# Quantidade de interfaces DOWN (com problemas) em cada switch
# Switch de acesso tem mais interfaces = mais chances de falha
interfaces_down = [2, 6, 4, 3, 6]

# ============================================================================
# DADOS DO GRÁFICO 3 - DISTRIBUIÇÃO DE VLANS
# ============================================================================

# VLANs configuradas na rede
# Padrão comum: 10=Dados, 20=VoIP, 30=WiFi, 40=Servidores, 99=Gerência
vlans = ['VLAN 10 - Dados', 'VLAN 20 - VoIP', 'VLAN 30 - WiFi',
         'VLAN 40 - Servidores', 'VLAN 99 - Gerência']

# Número de dispositivos conectados em cada VLAN
# VLAN Dados tem mais dispositivos (computadores, notebooks)
# VLAN Gerência tem menos (apenas equipamentos de rede)
num_dispositivos = [150, 80, 120, 35, 15]

# ============================================================================
# DADOS DO GRÁFICO 4 - UTILIZAÇÃO DE CPU
# ============================================================================

# Dispositivos críticos da infraestrutura
# RTR = Roteador, SW = Switch, FW = Firewall
dispositivos = ['RTR-CORE-01', 'RTR-EDGE-01', 'SW-CORE-01', 'FW-01', 'SW-DIST-01']

# Percentual de CPU de cada dispositivo
# Valores: <50% = OK (verde), 50-70% = Atenção (laranja), >70% = Crítico (vermelho)
cpu_percent = [45, 68, 32, 75, 28]

# ============================================================================
# CRIAR ESTRUTURA DO DASHBOARD (2x2 GRÁFICOS)
# ============================================================================

# make_subplots() cria uma grade de gráficos
# É como criar 4 "espaços" para colocar gráficos diferentes
fig = make_subplots(
    rows=2,                                     # 2 linhas de gráficos
    cols=2,                                     # 2 colunas de gráficos
    subplot_titles=(                            # Título de cada gráfico
        '📊 Tráfego de Rede - Últimas 24h',    # Linha 1, Coluna 1
        '🔌 Status de Interfaces por Switch',   # Linha 1, Coluna 2
        '🌐 Distribuição de Dispositivos por VLAN',  # Linha 2, Coluna 1
        '💻 Utilização de CPU - Dispositivos Críticos'  # Linha 2, Coluna 2
    ),
    specs=[                                     # Especifica tipo de cada gráfico
        [{'type': 'xy'}, {'type': 'xy'}],       # Linha 1: ambos tipo XY
        [{'type': 'xy'}, {'type': 'xy'}]        # Linha 2: ambos tipo XY
    ],                                          # IMPORTANTE: usar 'xy' para todos
                                                # Pizza será posicionada manualmente
    vertical_spacing=0.15,                      # Espaço vertical entre gráficos (15%)
    horizontal_spacing=0.25                     # Espaço horizontal entre gráficos (25%)
                                                # Aumentado para evitar sobreposição
)

# ============================================================================
# ADICIONAR GRÁFICO 1: LINHA - TRÁFEGO DE REDE
# ============================================================================

# add_trace() adiciona um elemento visual ao dashboard
# row=1, col=1 = primeira linha, primeira coluna (canto superior esquerdo)
fig.add_trace(
    go.Scatter(                                 # Scatter = gráfico de dispersão/linha
        x=horas,                                # Eixo X = horários
        y=trafego_mbps,                         # Eixo Y = tráfego em Mbps
        mode='lines+markers',                   # Desenha linha E pontos
        name='Tráfego (Mbps)',                  # Nome na legenda
        line=dict(
            color='#00CC96',                    # Cor verde (padrão Plotly)
            width=3                             # Espessura da linha
        ),
        marker=dict(size=6),                    # Tamanho dos pontos marcadores
        fill='tozeroy',                         # Preenche área até Y=0
        fillcolor='rgba(0,204,150,0.2)'         # Cor do preenchimento (verde transparente)
                                                # rgba() = Red, Green, Blue, Alpha (transparência)
    ),
    row=1, col=1                                # Posição no dashboard
)

# ============================================================================
# ADICIONAR GRÁFICO 2: BARRAS AGRUPADAS - STATUS DE INTERFACES
# ============================================================================

# PARTE 1: Barras verdes (interfaces UP)
fig.add_trace(
    go.Bar(                                     # Bar = gráfico de barras
        x=switches,                             # Eixo X = nomes dos switches
        y=interfaces_up,                        # Eixo Y = quantidade de interfaces UP
        name='UP',                              # Nome na legenda
        marker_color='#00CC96',                 # Cor verde = operacional
        text=interfaces_up,                     # Exibe valor dentro da barra
        textposition='inside'                   # Texto dentro da barra
    ),
    row=1, col=2                                # Linha 1, Coluna 2 (superior direito)
)

# PARTE 2: Barras vermelhas (interfaces DOWN)
# Ficarão lado a lado (barmode='group' no layout)
fig.add_trace(
    go.Bar(                                     # Mesma posição = agrupa automaticamente
        x=switches,                             # Mesmos switches
        y=interfaces_down,                      # Quantidade de interfaces DOWN
        name='DOWN',                            # Nome na legenda
        marker_color='#EF553B',                 # Cor vermelha = problema
        text=interfaces_down,                   # Exibe valor dentro da barra
        textposition='inside'                   # Texto dentro da barra
    ),
    row=1, col=2                                # Mesma posição = agrupa
)

# ============================================================================
# ADICIONAR GRÁFICO 3: PIZZA (DONUT) - DISTRIBUIÇÃO DE VLANS
# ============================================================================

# Pizza é adicionada SEM especificar row/col
# Será posicionada manualmente usando 'domain'
fig.add_trace(
    go.Pie(                                     # Pie = gráfico de pizza
        labels=vlans,                           # Rótulos de cada fatia
        values=num_dispositivos,                # Valores (tamanho das fatias)
        hole=0.4,                               # Buraco central = 40% (donut)
        name="Distribuição VLANs",              # Nome do gráfico
        marker=dict(
            colors=['#636EFA', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']
                                                # Cores customizadas para cada VLAN
        ),
        textinfo='label+percent'                # Mostra nome + percentual
    )
)

# IMPORTANTE: Posicionamento manual da pizza
# Define a posição da pizza no quadrante inferior esquerdo
# domain define a área onde o gráfico será desenhado
fig.update_traces(
    domain=dict(
        x=[0, 0.45],                            # Eixo X: 0% a 45% da largura
                                                # Ocupa metade esquerda
        y=[0, 0.4]                              # Eixo Y: 0% a 40% da altura
                                                # Ocupa parte inferior
    ),
    selector=dict(type='pie')                   # Aplica apenas ao gráfico de pizza
)

# ============================================================================
# ADICIONAR GRÁFICO 4: BARRAS HORIZONTAIS - UTILIZAÇÃO DE CPU
# ============================================================================

# Gerar cores dinamicamente baseado no percentual de CPU
# List comprehension que decide cor por valor:
# - Verde (#00CC96): CPU < 50%
# - Laranja (#FFA15A): 50% ≤ CPU < 70%
# - Vermelho (#EF553B): CPU ≥ 70%
cores_cpu = ['#00CC96' if cpu < 50 else '#FFA15A' if cpu < 70 else '#EF553B'
             for cpu in cpu_percent]

fig.add_trace(
    go.Bar(                                     # Bar = gráfico de barras
        x=cpu_percent,                          # Eixo X = percentual (horizontal!)
        y=dispositivos,                         # Eixo Y = nomes dos dispositivos
        orientation='h',                        # 'h' = horizontal (barras deitadas)
        marker=dict(
            color=cores_cpu                     # Lista de cores (uma por barra)
                                                # Cores são geradas dinamicamente acima
        ),
        text=[f'{cpu}%' for cpu in cpu_percent], # Adiciona "%" em cada valor
                                                # List comprehension formata texto
        textposition='outside',                 # Texto fora da barra (mais legível)
        showlegend=False                        # Não mostra na legenda (cores = info visual)
    ),
    row=2, col=2                                # Linha 2, Coluna 2 (inferior direito)
)

# ============================================================================
# CONFIGURAR EIXOS DE CADA GRÁFICO
# ============================================================================

# GRÁFICO 1 (Linha - Tráfego)
# update_xaxes() e update_yaxes() configuram os eixos de gráficos específicos
fig.update_xaxes(
    title_text="Hora",                          # Título do eixo X
    row=1, col=1                                # Gráfico específico (linha 1, coluna 1)
)
fig.update_yaxes(
    title_text="Mbps",                          # Título do eixo Y
    range=[0, 260],                             # Define escala fixa de 0 a 260 Mbps
                                                # Garante visualização completa dos dados
    row=1, col=1
)

# GRÁFICO 2 (Barras - Interfaces)
fig.update_xaxes(
    title_text="Switches",                      # Título do eixo X
    row=1, col=2                                # Gráfico das interfaces
)
fig.update_yaxes(
    title_text="Interfaces",                    # Título do eixo Y
    range=[0, 60],                              # Define escala de 0 a 60 interfaces
                                                # Acomoda barras empilhadas (UP + DOWN)
    row=1, col=2
)

# GRÁFICO 4 (Barras Horizontais - CPU)
fig.update_xaxes(
    title_text="CPU (%)",                       # Título do eixo X
    range=[0, 100],                             # Força escala de 0 a 100%
                                                # Sempre mostra escala completa
    row=2, col=2                                # Gráfico de CPU
)
fig.update_yaxes(
    title_text="",                              # Sem título (nomes já estão nos dispositivos)
    row=2, col=2
)

# ============================================================================
# CONFIGURAR LAYOUT GERAL DO DASHBOARD
# ============================================================================

# update_layout() personaliza a aparência geral do dashboard
fig.update_layout(
    title_text='🌐 Dashboard de Monitoramento de Rede - MVP',
                                                # Título principal do dashboard
    title_x=0.5,                                # Posição X = 50% (centralizado)
    title_font=dict(
        size=26,                                # Tamanho da fonte
        color='#2C3E50'                         # Cor azul escuro
    ),
    showlegend=True,                            # Mostrar legenda (importante!)
                                                # Legenda mostra UP/DOWN e VLANs
    height=950,                                 # Altura total do dashboard em pixels
                                                # Maior altura evita sobreposição
    plot_bgcolor='#F8F9FA',                     # Cor de fundo dos gráficos (cinza claro)
    paper_bgcolor='white',                      # Cor de fundo da página (branco)
    font=dict(
        family="Arial",                         # Fonte padrão para todo o dashboard
        size=12                                 # Tamanho padrão do texto
    ),
    barmode='group',                            # IMPORTANTE: barras lado a lado
                                                # 'group' = agrupadas (UP e DOWN separadas)
                                                # 'stack' = empilhadas (uma sobre a outra)
    annotations=[                               # Lista de anotações (textos extras)
        dict(
            text=f'Atualizado em: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}',
                                                # Texto com data/hora atual
                                                # strftime() formata: 19/10/2025 às 17:48:37
            xref='paper',                       # Referência X = página (coordenadas relativas)
            yref='paper',                       # Referência Y = página
            x=0.5,                              # Posição X = 50% (centro horizontal)
            y=-0.05,                            # Posição Y = -5% (abaixo dos gráficos)
                                                # Valor negativo coloca texto no rodapé
            xanchor='center',                   # Âncora horizontal no centro
            yanchor='top',                      # Âncora vertical no topo do texto
            showarrow=False,                    # Não mostrar seta apontando
            font=dict(
                size=11,                        # Tamanho menor que o texto principal
                color='#7F8C8D'                 # Cor cinza (menos destaque)
            )
        )
    ]
)

# ============================================================================
# EXPORTAR DASHBOARD PARA HTML
# ============================================================================

# write_html() salva o dashboard como página web interativa
# ../../ = sobe 2 níveis de diretório (de src/basico/ para raiz do projeto)
fig.write_html('../../docs/04_dashboard_mvp.html')

# Mensagens de confirmação no terminal
print("✅ Dashboard salvo em: 04_dashboard_mvp.html")

# Cálculo e exibição de estatísticas dos dados
print(f"📊 Total de dispositivos: {sum(num_dispositivos)}")
                                                # sum() soma todos os dispositivos das VLANs
print(f"🔌 Total de interfaces: {sum(interfaces_up) + sum(interfaces_down)}")
                                                # Soma interfaces UP + DOWN de todos switches
print(f"⚠️  Dispositivos críticos: {sum(1 for cpu in cpu_percent if cpu > 70)}")
                                                # Conta quantos dispositivos têm CPU > 70%
                                                # Generator expression com condicional

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Certifique-se de ter Plotly instalado:
   pip install plotly

2. Execute o script:
   python src/basico/04_dashboard_mvp_commented.py

3. Abra o arquivo gerado:
   docs/04_dashboard_mvp.html no navegador

4. Interaja com o dashboard:
   - Passe o mouse sobre gráficos para ver detalhes
   - Clique na legenda para ocultar/mostrar elementos
   - Use botões de zoom e pan (canto superior direito)
   - Clique e arraste para dar zoom em área específica
   - Duplo clique para resetar zoom

5. Experimente modificar:
   - Mude 'barmode' de 'group' para 'stack' (barras empilhadas)
   - Troque cores dos gráficos
   - Adicione mais dados (simule 48h ao invés de 24h)
   - Altere 'hole' da pizza para 0 (pizza cheia) ou 0.7 (anel fino)
   - Mude threshold de CPU (cores_cpu)
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ Criar dashboard com make_subplots()
✅ Usar specs com 'xy' para todos os gráficos
✅ Posicionar pizza manualmente com domain
✅ Combinar diferentes tipos de gráficos
✅ Barras agrupadas (barmode='group')
✅ Barras horizontais (orientation='h')
✅ Colorir dinamicamente com list comprehension
✅ Configurar eixos individualmente (update_xaxes, update_yaxes)
✅ Definir escalas fixas (range=[min, max])
✅ Formatar datas em Python (datetime, strftime)
✅ Adicionar anotações de rodapé
✅ Preencher área sob linha (fill='tozeroy')
✅ Calcular estatísticas com sum() e generator expressions

DIFERENÇAS IMPORTANTES:
- specs com 'xy': funciona para todos os tipos
- Pizza com domain: posicionamento manual preciso
- barmode='group': barras lado a lado (vs 'stack' empilhadas)
- Escalas fixas: garantem visualização consistente

QUANDO USAR DASHBOARD:
✅ Monitorar múltiplas métricas simultaneamente
✅ Visualizar correlações entre dados
✅ Apresentações executivas
✅ NOC (Network Operations Center)
✅ Relatórios gerenciais
✅ Troubleshooting de rede

PRÓXIMOS PASSOS:
- Adicionar mais gráficos (scatter, heatmap, gauge)
- Conectar com dados reais (SNMP, APIs, SSH)
- Implementar refresh automático
- Adicionar filtros interativos
- Criar alertas visuais dinâmicos
- Integrar com banco de dados
"""

# ============================================================================
# VARIAÇÕES POSSÍVEIS
# ============================================================================
"""
BARRAS EMPILHADAS (ao invés de agrupadas):
barmode='stack'  # Interfaces UP e DOWN uma sobre a outra

PIZZA CHEIA (sem buraco):
hole=0  # Remove o buraco central

CORES DIFERENTES PARA CPU:
cores_cpu = ['#2ECC71' if cpu < 40 else '#F39C12' if cpu < 60 
             else '#E74C3C' if cpu < 80 else '#C0392B' for cpu in cpu_percent]
# 4 níveis de cores ao invés de 3

ADICIONAR LINHA DE THRESHOLD NO GRÁFICO DE CPU:
fig.add_shape(
    type="line",
    x0=70, x1=70, y0=0, y1=1,
    xref="x4", yref="y4 domain",
    line=dict(color="red", width=2, dash="dash"),
    opacity=0.5
)

DASHBOARD VERTICAL (3 linhas x 1 coluna):
fig = make_subplots(rows=3, cols=1, ...)

DARK MODE:
plot_bgcolor='#1E1E1E'
paper_bgcolor='#000000'
font=dict(color='white')

TÍTULO COM MAIS INFORMAÇÕES:
title_text=f'Dashboard - {datetime.now().strftime("%A, %d de %B de %Y")}'
# Mostra dia da semana e mês por extenso
"""