#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico de Barras - Comparação de Labs por Domínio CCNP

Visualiza quantidade de labs completados em cada domínio do ENCOR 350-401.
Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-12
"""

import plotly.graph_objects as go

# Dados dos domínios CCNP ENCOR
dominios = [
    'Architecture',
    'Virtualization', 
    'Infrastructure',
    'Network Assurance',
    'Security',
    'Automation'
]

labs_completos = [24, 18, 6, 0, 0, 21]
peso_prova = [30, 10, 30, 10, 20, 15]  # Peso % na prova ENCOR

# Cores por domínio
cores = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a']

# Criar gráfico
fig = go.Figure()

# Adicionar barras
fig.add_trace(go.Bar(
    x=dominios,
    y=labs_completos,
    marker=dict(
        color=cores,
        line=dict(color='white', width=2)
    ),
    text=labs_completos,
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Labs: %{y}<extra></extra>'
))

# Configurar layout
fig.update_layout(
    title='Labs por Domínio CCNP ENCOR',
    xaxis_title='Domínio',
    yaxis_title='Número de Labs',
    template='plotly_white',
    height=500,
    showlegend=False,
    yaxis=dict(range=[0, max(labs_completos) + 5])
)

# Exportar
fig.write_html('../../docs/02_bar_chart.html')
print("✅ Gráfico salvo em: docs/02_bar_chart.html")