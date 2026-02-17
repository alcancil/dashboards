#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico Heatmap - Utilização de Dispositivos ao Longo do Tempo

Visualiza padrões de uso de CPU/Memória em dispositivos de rede durante 24h.
Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-20
"""

import plotly.graph_objects as go
import random

# Seed para reprodutibilidade
random.seed(42)

# Lista de dispositivos monitorados
dispositivos = [
    'RTR-CORE-01',
    'RTR-EDGE-01',
    'SW-CORE-01',
    'SW-DIST-01',
    'SW-DIST-02',
    'SW-ACCESS-01',
    'SW-ACCESS-02',
    'FW-01',
    'FW-02',
    'LB-01'
]

# Horas do dia (0-23)
horas = [f'{h:02d}:00' for h in range(24)]

# Gerar dados de utilização (matriz 10x24)
utilizacao_data = []

for dispositivo in dispositivos:
    utilizacao_hora = []
    
    for hora in range(24):
        # Padrões realistas por horário
        if 0 <= hora < 6:  # Madrugada
            base = random.uniform(10, 25)
        elif 6 <= hora < 9:  # Início manhã
            base = random.uniform(30, 50)
        elif 9 <= hora < 12:  # Manhã comercial
            base = random.uniform(50, 75)
        elif 12 <= hora < 14:  # Almoço
            base = random.uniform(40, 60)
        elif 14 <= hora < 18:  # Tarde comercial
            base = random.uniform(60, 85)
        elif 18 <= hora < 21:  # Início noite
            base = random.uniform(35, 55)
        else:  # Noite
            base = random.uniform(15, 35)
        
        # Ajustar por tipo de dispositivo
        if 'FW' in dispositivo:  # Firewalls sempre mais carregados
            base += random.uniform(10, 20)
        elif 'RTR-CORE' in dispositivo:  # Core routers
            base += random.uniform(5, 15)
        elif 'ACCESS' in dispositivo:  # Switches de acesso
            base += random.uniform(0, 10)
        
        # Garantir que fica entre 0-100%
        utilizacao = min(100, max(0, base))
        utilizacao_hora.append(round(utilizacao, 1))
    
    utilizacao_data.append(utilizacao_hora)

# Criar heatmap
fig = go.Figure(data=go.Heatmap(
    z=utilizacao_data,
    x=horas,
    y=dispositivos,
    colorscale=[
        [0.0, '#2ecc71'],    # Verde (0-33%)
        [0.33, '#f39c12'],   # Laranja (33-66%)
        [0.66, '#e74c3c'],   # Vermelho (66-100%)
        [1.0, '#c0392b']     # Vermelho escuro (>90%)
    ],
    colorbar=dict(
        title=dict(
            text='Utilização<br>(%)',
            side='right'
        ),
        tickmode='linear',
        tick0=0,
        dtick=20
    ),
    hovertemplate=(
        '<b>%{y}</b><br>' +
        'Hora: %{x}<br>' +
        'Utilização: %{z}%<br>' +
        '<extra></extra>'
    ),
    text=[[f'{val:.0f}%' for val in linha] for linha in utilizacao_data],
    texttemplate='%{text}',
    textfont={'size': 9, 'color': 'white'},
    showscale=True
))

# Configurar layout
fig.update_layout(
    title='Mapa de Calor - Utilização de Dispositivos (24h)',
    xaxis=dict(
        title='Hora do Dia',
        side='bottom',
        tickangle=0
    ),
    yaxis=dict(
        title='Dispositivos',
        autorange='reversed'
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family='Arial', size=12),
    height=600,
    margin=dict(l=120, r=100, t=80, b=80)
)

# Adicionar anotações de zonas de horário
fig.add_annotation(
    x=3, y=-1.5,
    text='Madrugada',
    showarrow=False,
    font=dict(size=10, color='gray'),
    xref='x', yref='y'
)

fig.add_annotation(
    x=10, y=-1.5,
    text='Horário Comercial',
    showarrow=False,
    font=dict(size=10, color='gray'),
    xref='x', yref='y'
)

fig.add_annotation(
    x=19, y=-1.5,
    text='Noite',
    showarrow=False,
    font=dict(size=10, color='gray'),
    xref='x', yref='y'
)

# Exportar
fig.write_html('../../docs/06_heatmap_devices.html')
print("✅ Heatmap salvo em: docs/06_heatmap_devices.html")
print(f"📊 Dispositivos monitorados: {len(dispositivos)}")
print(f"⏰ Período: 24 horas")

# Calcular estatísticas
utilizacao_maxima = max(max(linha) for linha in utilizacao_data)
utilizacao_minima = min(min(linha) for linha in utilizacao_data)
utilizacao_media = sum(sum(linha) for linha in utilizacao_data) / (len(dispositivos) * 24)

print(f"📈 Utilização máxima: {utilizacao_maxima:.1f}%")
print(f"📉 Utilização mínima: {utilizacao_minima:.1f}%")
print(f"📊 Utilização média: {utilizacao_media:.1f}%")