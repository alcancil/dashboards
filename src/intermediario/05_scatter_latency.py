#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico Scatter - Análise de Latência vs Perda de Pacotes

Correlaciona latência e perda de pacotes em diferentes tipos de links.
Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-20
"""

import plotly.graph_objects as go
import random

# Seed para reprodutibilidade
random.seed(42)

# Gerar dados simulados de 50 links
links_data = []
tipos_link = ['Fibra', 'Wireless', 'MPLS', 'Internet']
cores_tipos = {
    'Fibra': '#00CC96',      # Verde (melhor performance)
    'Wireless': '#FFA15A',   # Laranja (performance média)
    'MPLS': '#636EFA',       # Azul (corporativo)
    'Internet': '#EF553B'    # Vermelho (mais variável)
}

for i in range(50):
    tipo = random.choice(tipos_link)
    
    # Simular características por tipo de link
    if tipo == 'Fibra':
        latencia = random.uniform(5, 30)
        perda = random.uniform(0, 1)
        trafego = random.uniform(100, 500)
    elif tipo == 'Wireless':
        latencia = random.uniform(15, 80)
        perda = random.uniform(0.5, 5)
        trafego = random.uniform(20, 200)
    elif tipo == 'MPLS':
        latencia = random.uniform(10, 50)
        perda = random.uniform(0, 2)
        trafego = random.uniform(50, 300)
    else:  # Internet
        latencia = random.uniform(30, 150)
        perda = random.uniform(1, 8)
        trafego = random.uniform(10, 150)
    
    links_data.append({
        'nome': f'Link-{i+1:02d}',
        'tipo': tipo,
        'latencia_ms': round(latencia, 2),
        'perda_pacotes': round(perda, 2),
        'trafego_mbps': round(trafego, 2)
    })

# Criar figura
fig = go.Figure()

# Adicionar scatter por tipo de link
for tipo in tipos_link:
    links_tipo = [link for link in links_data if link['tipo'] == tipo]
    
    fig.add_trace(go.Scatter(
        x=[link['latencia_ms'] for link in links_tipo],
        y=[link['perda_pacotes'] for link in links_tipo],
        mode='markers',
        name=tipo,
        marker=dict(
            size=[link['trafego_mbps'] / 10 for link in links_tipo],
            color=cores_tipos[tipo],
            opacity=0.7,
            line=dict(color='white', width=1)
        ),
        text=[f"{link['nome']}<br>Tráfego: {link['trafego_mbps']} Mbps" 
              for link in links_tipo],
        hovertemplate=(
            '<b>%{text}</b><br>' +
            'Latência: %{x} ms<br>' +
            'Perda: %{y}%<br>' +
            '<extra></extra>'
        )
    ))

# Configurar layout
fig.update_layout(
    title='Análise de Performance de Links de Rede',
    xaxis=dict(
        title='Latência (ms)',
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True,
        zeroline=False
    ),
    yaxis=dict(
        title='Perda de Pacotes (%)',
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True,
        zeroline=False
    ),
    plot_bgcolor='#F8F9FA',
    paper_bgcolor='white',
    font=dict(family='Arial', size=12),
    hovermode='closest',
    showlegend=True,
    legend=dict(
        title='Tipo de Link',
        orientation='v',
        yanchor='top',
        y=1,
        xanchor='left',
        x=1.02
    ),
    height=600
)

# Adicionar anotações de zonas
fig.add_shape(
    type="rect",
    x0=0, x1=50, y0=0, y1=2,
    fillcolor="green",
    opacity=0.1,
    layer="below",
    line_width=0
)

fig.add_annotation(
    x=25, y=1,
    text="Zona Ótima",
    showarrow=False,
    font=dict(size=10, color='green'),
    opacity=0.5
)

# Exportar
fig.write_html('../../docs/05_scatter_latency.html')
print("✅ Gráfico salvo em: docs/05_scatter_latency.html")
print(f"📊 Total de links analisados: {len(links_data)}")
print(f"🔍 Tipos de link: {', '.join(tipos_link)}")