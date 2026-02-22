#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Intermediário - Monitoramento Completo com Filtros

Integra 4 gráficos intermediários com controles interativos.
Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-20
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import datetime, timedelta

# Seed para reprodutibilidade
random.seed(42)

# ============================================================================
# DADOS - SCATTER (LATÊNCIA)
# ============================================================================

tipos_link = ['Fibra', 'Wireless', 'MPLS', 'Internet']
cores_tipos = {
    'Fibra': '#00CC96',
    'Wireless': '#FFA15A',
    'MPLS': '#636EFA',
    'Internet': '#EF553B'
}

links_scatter = []
for i in range(50):
    tipo = random.choice(tipos_link)
    if tipo == 'Fibra':
        latencia = random.uniform(5, 30)
        perda = random.uniform(0, 1)
    elif tipo == 'Wireless':
        latencia = random.uniform(15, 80)
        perda = random.uniform(0.5, 5)
    elif tipo == 'MPLS':
        latencia = random.uniform(10, 50)
        perda = random.uniform(0, 2)
    else:
        latencia = random.uniform(30, 150)
        perda = random.uniform(1, 8)
    
    links_scatter.append({
        'tipo': tipo,
        'latencia': round(latencia, 2),
        'perda': round(perda, 2)
    })

# ============================================================================
# DADOS - HEATMAP (UTILIZAÇÃO)
# ============================================================================

dispositivos = ['RTR-CORE-01', 'RTR-EDGE-01', 'SW-CORE-01', 'SW-DIST-01', 
                'FW-01', 'LB-01']
horas = [f'{h:02d}:00' for h in range(24)]

utilizacao_data = []
for dispositivo in dispositivos:
    utilizacao_hora = []
    for hora in range(24):
        if 0 <= hora < 6:
            base = random.uniform(10, 25)
        elif 6 <= hora < 9:
            base = random.uniform(30, 50)
        elif 9 <= hora < 18:
            base = random.uniform(50, 85)
        else:
            base = random.uniform(15, 35)
        
        if 'FW' in dispositivo:
            base += random.uniform(10, 20)
        
        utilizacao_hora.append(round(min(100, max(0, base)), 1))
    utilizacao_data.append(utilizacao_hora)

# ============================================================================
# DADOS - GAUGE (BANDA)
# ============================================================================

links_gauge = [
    {'nome': 'Link Principal', 'capacidade': 1000, 'utilizado': 650},
    {'nome': 'Link Backup', 'capacidade': 500, 'utilizado': 180},
    {'nome': 'Link Core', 'capacidade': 10000, 'utilizado': 5200},
    {'nome': 'Link VPN', 'capacidade': 200, 'utilizado': 165}
]

for link in links_gauge:
    link['percentual'] = round((link['utilizado'] / link['capacidade']) * 100, 1)

# ============================================================================
# CRIAR DASHBOARD 2x2
# ============================================================================

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        '📊 Latência vs Perda de Pacotes',
        '🔥 Utilização de Dispositivos (24h)',
        '📡 Utilização de Banda',
        '📋 Resumo de Status'
    ),
    specs=[
        [{'type': 'scatter'}, {'type': 'heatmap'}],
        [{'type': 'indicator'}, {'type': 'table'}]
    ],
    vertical_spacing=0.15,
    horizontal_spacing=0.12
)

# ============================================================================
# GRÁFICO 1: SCATTER
# ============================================================================

for tipo in tipos_link:
    links_tipo = [l for l in links_scatter if l['tipo'] == tipo]
    fig.add_trace(
        go.Scatter(
            x=[l['latencia'] for l in links_tipo],
            y=[l['perda'] for l in links_tipo],
            mode='markers',
            name=tipo,
            marker=dict(size=8, color=cores_tipos[tipo], opacity=0.7),
            hovertemplate=f'<b>{tipo}</b><br>Latência: %{{x}}ms<br>Perda: %{{y}}%<extra></extra>'
        ),
        row=1, col=1
    )

fig.update_xaxes(title_text="Latência (ms)", row=1, col=1)
fig.update_yaxes(title_text="Perda (%)", row=1, col=1)

# ============================================================================
# GRÁFICO 2: HEATMAP
# ============================================================================

fig.add_trace(
    go.Heatmap(
        z=utilizacao_data,
        x=horas,
        y=dispositivos,
        colorscale=[[0, '#2ecc71'], [0.5, '#f39c12'], [1, '#e74c3c']],
        showscale=False,
        hovertemplate='<b>%{y}</b><br>Hora: %{x}<br>Utilização: %{z}%<extra></extra>'
    ),
    row=1, col=2
)

fig.update_xaxes(title_text="Hora", row=1, col=2)
fig.update_yaxes(title_text="Dispositivos", row=1, col=2)

# ============================================================================
# GRÁFICO 3: GAUGE (RESUMO)
# ============================================================================

media_utilizacao = sum(l['percentual'] for l in links_gauge) / len(links_gauge)

fig.add_trace(
    go.Indicator(
        mode='gauge+number',
        value=round(media_utilizacao, 1),
        title={'text': 'Utilização Média de Banda'},
        number={'suffix': '%', 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': 'darkblue'},
            'steps': [
                {'range': [0, 50], 'color': '#2ecc71'},
                {'range': [50, 80], 'color': '#f39c12'},
                {'range': [80, 100], 'color': '#e74c3c'}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ),
    row=2, col=1
)

# ============================================================================
# GRÁFICO 4: TABELA RESUMO
# ============================================================================

fig.add_trace(
    go.Table(
        header=dict(
            values=['<b>Link</b>', '<b>Capacidade</b>', '<b>Usado</b>', '<b>Status</b>'],
            fill_color='#3498db',
            font=dict(color='white', size=12),
            align='left'
        ),
        cells=dict(
            values=[
                [l['nome'] for l in links_gauge],
                [f"{l['capacidade']} Mbps" for l in links_gauge],
                [f"{l['utilizado']} Mbps ({l['percentual']}%)" for l in links_gauge],
                ['🟢' if l['percentual'] < 50 else '🟡' if l['percentual'] < 80 else '🔴' 
                 for l in links_gauge]
            ],
            fill_color=[['#ecf0f1', 'white'] * 2],
            align='left',
            font=dict(size=11)
        )
    ),
    row=2, col=2
)

# ============================================================================
# LAYOUT
# ============================================================================

fig.update_layout(
    title={
        'text': '📊 Dashboard Intermediário - Monitoramento de Rede<br>' +
                f'<sub>Atualizado: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</sub>',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 24}
    },
    height=900,
    showlegend=True,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    plot_bgcolor='#F8F9FA',
    paper_bgcolor='white',
    font=dict(family='Arial', size=12)
)

# Exportar
fig.write_html('../../docs/09_dashboard_intermediario.html')
print("✅ Dashboard salvo em: docs/09_dashboard_intermediario.html")
print(f"\n📊 Resumo do Dashboard:")
print(f"  📈 Links analisados: {len(links_scatter)}")
print(f"  🖥️  Dispositivos monitorados: {len(dispositivos)}")
print(f"  📡 Links de banda: {len(links_gauge)}")
print(f"  📊 Utilização média: {media_utilizacao:.1f}%")