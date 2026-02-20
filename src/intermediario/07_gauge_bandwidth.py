#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico Gauge - Medidor de Banda de Links

Visualiza utilização atual de banda em diferentes links de rede.
Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-20
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# Seed para reprodutibilidade
random.seed(42)

# Dados dos links (nome, capacidade Mbps, utilização atual Mbps)
links = [
    {
        'nome': 'Link Principal',
        'tipo': 'Internet',
        'capacidade': 1000,
        'utilizado': random.randint(500, 850)
    },
    {
        'nome': 'Link Backup',
        'tipo': 'MPLS',
        'capacidade': 500,
        'utilizado': random.randint(100, 300)
    },
    {
        'nome': 'Link Interno',
        'tipo': 'Core',
        'capacidade': 10000,
        'utilizado': random.randint(3000, 7000)
    },
    {
        'nome': 'Link VPN',
        'tipo': 'Site-to-Site',
        'capacidade': 200,
        'utilizado': random.randint(50, 180)
    }
]

# Calcular percentuais
for link in links:
    link['percentual'] = round((link['utilizado'] / link['capacidade']) * 100, 1)

# Criar subplot 2x2
fig = make_subplots(
    rows=2, cols=2,
    specs=[
        [{'type': 'indicator'}, {'type': 'indicator'}],
        [{'type': 'indicator'}, {'type': 'indicator'}]
    ],
    subplot_titles=[f"{link['nome']}<br><sub>{link['tipo']}</sub>" for link in links],
    vertical_spacing=0.25,
    horizontal_spacing=0.15
)

# Adicionar gauges
positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

for idx, (link, pos) in enumerate(zip(links, positions)):
    fig.add_trace(
        go.Indicator(
            mode='gauge+number+delta',
            value=link['percentual'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={
                'text': f"{link['utilizado']} Mbps",
                'font': {'size': 14}
            },
            delta={
                'reference': 80,
                'increasing': {'color': 'red'},
                'decreasing': {'color': 'green'}
            },
            number={
                'suffix': '%',
                'font': {'size': 40}
            },
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickwidth': 1,
                    'tickcolor': 'darkgray'
                },
                'bar': {'color': 'darkblue'},
                'bgcolor': 'white',
                'borderwidth': 2,
                'bordercolor': 'gray',
                'steps': [
                    {'range': [0, 50], 'color': '#2ecc71'},      # Verde
                    {'range': [50, 80], 'color': '#f39c12'},     # Laranja
                    {'range': [80, 100], 'color': '#e74c3c'}     # Vermelho
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ),
        row=pos[0], col=pos[1]
    )
    
    # Adicionar anotação de capacidade
    fig.add_annotation(
        text=f'Capacidade: {link["capacidade"]} Mbps',
        xref=f'x{idx+1}' if idx > 0 else 'x',
        yref=f'y{idx+1}' if idx > 0 else 'y',
        x=0.5, y=-0.3,
        showarrow=False,
        font=dict(size=11, color='gray')
    )

# Layout
fig.update_layout(
    title={
        'text': '📊 Monitoramento de Banda - Links de Rede',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 24}
    },
    height=800,
    showlegend=False,
    paper_bgcolor='white',
    font=dict(family='Arial', size=12)
)

# Exportar
fig.write_html('../../docs/07_gauge_bandwidth.html')
print("✅ Gauge salvo em: docs/07_gauge_bandwidth.html")
print(f"\n📊 Status dos Links:")
for link in links:
    status = '🟢' if link['percentual'] < 50 else '🟡' if link['percentual'] < 80 else '🔴'
    print(f"{status} {link['nome']}: {link['utilizado']}/{link['capacidade']} Mbps ({link['percentual']}%)")