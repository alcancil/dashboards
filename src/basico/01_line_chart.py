#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico de Linha - Progresso Semanal de Labs (VERSÃO DIDÁTICA)

Cria visualização do progresso de labs CCNP ao longo das semanas.
Esta versão contém comentários linha a linha para aprendizado.

Autor: Alexandre Cancilieri
Data: 2025-10-11
"""

import plotly.graph_objects as go  

# Dados
semanas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
labs_completos = [2, 5, 8, 12, 15, 20, 24, 28, 32, 38, 45, 52]

# Criar gráfico
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=semanas,                           
    y=labs_completos,                    
    mode='lines+markers',                
    name='Labs Completos',               
    line=dict(
        color='#667eea',               
        width=3                          
    ),
    marker=dict(
        size=10,                         
        color='#667eea'                
    )
))

# Configurar layout
fig.update_layout(
    title='Progresso de Labs CCNP - 12 Semanas',   
    xaxis_title='Semana',                          
    yaxis_title='Total de Labs Completos',         
    hovermode='x unified',                         
    template='plotly_white',                       
    height=500                                     
)

# Exportar
fig.write_html('../../docs/01_line_chart.html')

print("✅ Gráfico salvo em: docs/01_line_chart.html")