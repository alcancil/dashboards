#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico de Pizza - Distribuição de Labs por Categoria

Visualiza a proporção de labs em diferentes categorias de conteúdo.
Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-12
"""

import plotly.graph_objects as go

# Dados das categorias
categorias = [
    'QoS',
    'VRF-Lite',
    'Python/Automação',
    'Multicast',
    'Virtualização',
    'Outros'
]

quantidade = [24, 4, 21, 4, 18, 8]

# Cores por categoria
cores = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a']

# Criar gráfico
fig = go.Figure()

# Adicionar pizza (donut)
fig.add_trace(go.Pie(
    labels=categorias,
    values=quantidade,
    marker=dict(
        colors=cores,
        line=dict(color='white', width=2)
    ),
    hole=0.4,  # Tamanho do buraco (0 = pizza cheia, 0.4 = donut)
    textposition='auto',
    textinfo='label+percent',
    hovertemplate='<b>%{label}</b><br>Labs: %{value}<br>Percentual: %{percent}<extra></extra>'
))

# Configurar layout
fig.update_layout(
    title='Distribuição de Labs por Categoria',
    template='plotly_white',
    height=500,
    showlegend=True,
    legend=dict(
        orientation="v",
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=1.05
    )
)

# Adicionar anotação no centro do donut
fig.add_annotation(
    text=f'<b>{sum(quantidade)}</b><br>Labs<br>Total',
    x=0.5,
    y=0.5,
    font=dict(size=20, color='#667eea'),
    showarrow=False
)

# Exportar
fig.write_html('../../docs/03_pie_chart.html')
print("✅ Gráfico salvo em: docs/03_pie_chart.html")