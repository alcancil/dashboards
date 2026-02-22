#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico Interativo - Filtros Linkados de Latência e Performance

Visualiza latência vs perda de pacotes com controles interativos:
dropdown (região), botões de toggle (tipo de link) e range slider (latência).
Dois subplots linkados: scatter e box plot de distribuição.

Autor: Alexandre Lavorenti Cancilieri
Data: 2026-02-22
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

random.seed(42)

# ============================================================================
# DADOS
# ============================================================================

tipos_link = ['Fibra', 'Wireless', 'MPLS', 'Internet']

cores_tipos = {
    'Fibra':    '#00CC96',
    'Wireless': '#FFA15A',
    'MPLS':     '#636EFA',
    'Internet': '#EF553B'
}

regioes = ['Sudeste', 'Sul', 'Nordeste', 'Centro-Oeste', 'Norte']

links = []
for i in range(100):
    tipo   = random.choice(tipos_link)
    regiao = random.choice(regioes)

    if tipo == 'Fibra':
        latencia  = random.uniform(5, 30)
        perda     = random.uniform(0, 1)
        bandwidth = random.uniform(500, 1000)
    elif tipo == 'Wireless':
        latencia  = random.uniform(15, 80)
        perda     = random.uniform(0.5, 5)
        bandwidth = random.uniform(50, 300)
    elif tipo == 'MPLS':
        latencia  = random.uniform(10, 50)
        perda     = random.uniform(0, 2)
        bandwidth = random.uniform(200, 600)
    else:
        latencia  = random.uniform(30, 150)
        perda     = random.uniform(1, 8)
        bandwidth = random.uniform(10, 100)

    links.append({
        'id':        f'LINK-{i+1:03d}',
        'tipo':      tipo,
        'regiao':    regiao,
        'latencia':  round(latencia, 2),
        'perda':     round(perda, 2),
        'bandwidth': round(bandwidth, 1)
    })

# ============================================================================
# FIGURA BASE COM SUBPLOTS
# ============================================================================

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=(
        '🔵 Latência vs Perda de Pacotes',
        '📊 Distribuição de Latência por Tipo'
    ),
    column_widths=[0.6, 0.4],
    horizontal_spacing=0.12
)

# ============================================================================
# SUBPLOT 1: SCATTER - LATÊNCIA vs PERDA
# ============================================================================

for tipo in tipos_link:
    dados_tipo = [l for l in links if l['tipo'] == tipo]
    fig.add_trace(
        go.Scatter(
            x=[l['latencia'] for l in dados_tipo],
            y=[l['perda']    for l in dados_tipo],
            mode='markers',
            name=tipo,
            legendgroup=tipo,
            marker=dict(
                size=[max(8, l['bandwidth'] / 40) for l in dados_tipo],
                color=cores_tipos[tipo],
                opacity=0.75,
                line=dict(width=1, color='white')
            ),
            text=[
                f"ID: {l['id']}<br>Região: {l['regiao']}<br>Bandwidth: {l['bandwidth']} Mbps"
                for l in dados_tipo
            ],
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Latência: %{x} ms<br>'
                'Perda: %{y}%<br>'
                '<extra>' + tipo + '</extra>'
            )
        ),
        row=1, col=1
    )

# Zona de performance ótima (background verde sutil)
fig.add_shape(
    type='rect',
    x0=0, y0=0, x1=50, y1=2,
    fillcolor='rgba(0, 204, 150, 0.08)',
    line=dict(color='rgba(0, 204, 150, 0.5)', dash='dot'),
    row=1, col=1
)
fig.add_annotation(
    x=25, y=1,
    text='✅ Zona Ótima',
    showarrow=False,
    font=dict(size=10, color='#00CC96'),
    row=1, col=1
)

fig.update_xaxes(title_text='Latência (ms)', range=[0, 160], row=1, col=1)
fig.update_yaxes(title_text='Perda de Pacotes (%)', row=1, col=1)

# ============================================================================
# SUBPLOT 2: BOX PLOT - DISTRIBUIÇÃO DE LATÊNCIA
# ============================================================================

for tipo in tipos_link:
    dados_tipo = [l for l in links if l['tipo'] == tipo]
    fig.add_trace(
        go.Box(
            y=[l['latencia'] for l in dados_tipo],
            name=tipo,
            legendgroup=tipo,
            showlegend=False,
            marker_color=cores_tipos[tipo],
            boxmean='sd',
            hovertemplate=(
                '<b>' + tipo + '</b><br>'
                'Mediana: %{median} ms<br>'
                'Q1: %{q1} ms | Q3: %{q3} ms<br>'
                '<extra></extra>'
            )
        ),
        row=1, col=2
    )

fig.update_yaxes(title_text='Latência (ms)', row=1, col=2)

# ============================================================================
# DROPDOWN - FILTRO POR REGIÃO
# Usa method='restyle' para atualizar os dados x/y de cada trace
# ============================================================================

botoes_regiao = []
opcoes_regiao = ['Todas as Regiões'] + regioes

for opcao in opcoes_regiao:
    novos_x_scatter, novos_y_scatter = [], []
    novos_text_scatter, novos_size_scatter = [], []
    novos_y_box = []

    for tipo in tipos_link:
        if opcao == 'Todas as Regiões':
            filtrado = [l for l in links if l['tipo'] == tipo]
        else:
            filtrado = [l for l in links if l['tipo'] == tipo and l['regiao'] == opcao]

        novos_x_scatter.append([l['latencia'] for l in filtrado])
        novos_y_scatter.append([l['perda']    for l in filtrado])
        novos_text_scatter.append([
            f"ID: {l['id']}<br>Região: {l['regiao']}<br>Bandwidth: {l['bandwidth']} Mbps"
            for l in filtrado
        ])
        novos_size_scatter.append([max(8, l['bandwidth'] / 40) for l in filtrado])
        novos_y_box.append([l['latencia'] for l in filtrado])

    botoes_regiao.append(dict(
        label=opcao,
        method='restyle',
        # Dois pares [dados, índices]: primeiro os scatter, depois os box
        # Separar por índice garante que cada grupo receba apenas seus dados
        args=[
            {
                'x':           novos_x_scatter,
                'y':           novos_y_scatter,
                'text':        novos_text_scatter,
                'marker.size': novos_size_scatter,
            },
            [0, 1, 2, 3]   # índices dos traces scatter
        ],
        args2=[
            {'y': novos_y_box},
            [4, 5, 6, 7]   # índices dos traces box
        ]
    ))

# ============================================================================
# BOTÕES TOGGLE - FILTRO POR TIPO DE LINK
# Usa method='update' para controlar visibilidade dos traces
# ============================================================================

n = len(tipos_link)

botoes_tipo = [dict(
    label='Todos',
    method='update',
    args=[{'visible': [True] * (n * 2)}]
)]

for i, tipo in enumerate(tipos_link):
    vis = [False] * (n * 2)
    vis[i]     = True   # scatter do tipo i
    vis[i + n] = True   # box do tipo i
    botoes_tipo.append(dict(
        label=tipo,
        method='update',
        args=[{'visible': vis}]
    ))

# ============================================================================
# RANGE SLIDER - FAIXA DE LATÊNCIA (eixo X do scatter)
# Usa method='relayout' para alterar range do eixo X
# ============================================================================

faixas_latencia = [
    ('0–50 ms',   [0,  50]),
    ('0–80 ms',   [0,  80]),
    ('0–150 ms',  [0, 150]),
    ('50–150 ms', [50, 150]),
]

steps_slider = []
for label, rng in faixas_latencia:
    steps_slider.append(dict(
        label=label,
        method='relayout',
        args=[{'xaxis.range': rng}]
    ))

# ============================================================================
# LAYOUT GLOBAL + CONTROLES
# ============================================================================

fig.update_layout(
    title=dict(
        text=(
            '🔍 Análise Interativa de Performance de Links<br>'
            '<sub>Use os controles abaixo para filtrar por região, tipo e faixa de latência</sub>'
        ),
        x=0.5,
        xanchor='center',
        font=dict(size=20)
    ),
    height=650,
    plot_bgcolor='#F8F9FA',
    paper_bgcolor='white',
    font=dict(family='Arial', size=12),
    legend=dict(
        title=dict(text='Tipo de Link'),
        orientation='h',
        yanchor='bottom',
        y=1.10,
        xanchor='center',
        x=0.5
    ),
    hovermode='closest',
    margin=dict(t=180, b=120),

    updatemenus=[
        # Dropdown: Região
        dict(
            buttons=botoes_regiao,
            direction='down',
            showactive=True,
            x=0.00, xanchor='left',
            y=1.30, yanchor='top',
            bgcolor='white',
            bordercolor='#aaaaaa',
            font=dict(size=12)
        ),
        # Botões Toggle: Tipo de Link
        dict(
            buttons=botoes_tipo,
            type='buttons',
            direction='right',
            showactive=True,
            x=0.50, xanchor='center',
            y=1.30, yanchor='top',
            bgcolor='#F0F0F0',
            bordercolor='#aaaaaa',
            font=dict(size=11)
        ),
    ],

    sliders=[dict(
        steps=steps_slider,
        active=2,
        currentvalue=dict(
            prefix='Faixa de Latência: ',
            font=dict(size=12, color='#333'),
            xanchor='center',
            visible=True
        ),
        x=0.00, len=0.60,
        y=-0.18,
        pad=dict(t=30, b=10),
        bgcolor='#F0F0F0',
        bordercolor='#aaaaaa',
        tickcolor='#888888',
        font=dict(size=11)
    )],

    annotations=[
        dict(
            text='🌎 Filtrar por Região:',
            x=0.00, y=1.35,
            xref='paper', yref='paper',
            showarrow=False,
            font=dict(size=11, color='#444')
        ),
        dict(
            text='🔗 Filtrar por Tipo:',
            x=0.38, y=1.35,
            xref='paper', yref='paper',
            showarrow=False,
            font=dict(size=11, color='#444')
        ),
    ]
)

# ============================================================================
# EXPORTAR
# ============================================================================

fig.write_html('../../docs/10_interactive_filters.html')
print("✅ Gráfico salvo em: docs/10_interactive_filters.html")
print(f"\n📊 Resumo:")
print(f"  🔗 Total de links simulados : {len(links)}")
print(f"  📡 Tipos de link            : {', '.join(tipos_link)}")
print(f"  🌎 Regiões                  : {', '.join(regioes)}")
print(f"  🎛️  Controles               : Dropdown (região) | Toggle (tipo) | Slider (latência)")