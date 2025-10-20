#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard MVP - Monitoramento de Rede (versão corrigida e funcional)
Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-19
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# --- Dados simulados ---

# Tráfego de rede (24 horas)
horas = [(datetime.now() - timedelta(hours=i)).strftime('%H:%M') for i in range(23, -1, -1)]
trafego_mbps = [120, 135, 145, 150, 160, 155, 170, 180, 190, 185,
                200, 210, 220, 230, 240, 235, 225, 215, 205, 195,
                180, 170, 150, 140]

# Status de interfaces
switches = ['SW-CORE-01', 'SW-DIST-01', 'SW-DIST-02', 'SW-ACCESS-01', 'SW-ACCESS-02']
interfaces_up = [22, 18, 20, 45, 42]
interfaces_down = [2, 6, 4, 3, 6]

# Distribuição de VLANs
vlans = ['VLAN 10 - Dados', 'VLAN 20 - VoIP', 'VLAN 30 - WiFi',
         'VLAN 40 - Servidores', 'VLAN 99 - Gerência']
num_dispositivos = [150, 80, 120, 35, 15]

# Utilização de CPU
dispositivos = ['RTR-CORE-01', 'RTR-EDGE-01', 'SW-CORE-01', 'FW-01', 'SW-DIST-01']
cpu_percent = [45, 68, 32, 75, 28]

# --- Criação dos subplots ---
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        '📊 Tráfego de Rede - Últimas 24h',
        '🔌 Status de Interfaces por Switch',
        '🌐 Distribuição de Dispositivos por VLAN',
        '💻 Utilização de CPU - Dispositivos Críticos'
    ),
    specs=[[{'type': 'xy'}, {'type': 'xy'}],
           [{'type': 'xy'}, {'type': 'xy'}]],  # <-- todos "xy" (nada de domain)
    vertical_spacing=0.15,
    horizontal_spacing=0.25
)

# --- Gráfico 1: Linha de tráfego ---
fig.add_trace(
    go.Scatter(
        x=horas,
        y=trafego_mbps,
        mode='lines+markers',
        name='Tráfego (Mbps)',
        line=dict(color='#00CC96', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(0,204,150,0.2)'
    ),
    row=1, col=1
)

# --- Gráfico 2: Barras de interfaces ---
fig.add_trace(
    go.Bar(
        x=switches,
        y=interfaces_up,
        name='UP',
        marker_color='#00CC96',
        text=interfaces_up,
        textposition='inside'
    ),
    row=1, col=2
)

fig.add_trace(
    go.Bar(
        x=switches,
        y=interfaces_down,
        name='DOWN',
        marker_color='#EF553B',
        text=interfaces_down,
        textposition='inside'
    ),
    row=1, col=2
)

# --- Gráfico 3: Pizza manual (posicionada via domain) ---
fig.add_trace(
    go.Pie(
        labels=vlans,
        values=num_dispositivos,
        hole=0.4,
        name="Distribuição VLANs",
        marker=dict(colors=['#636EFA', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']),
        textinfo='label+percent'
    )
)

# Define a posição da pizza no quadrante inferior esquerdo
fig.update_traces(domain=dict(x=[0, 0.45], y=[0, 0.4]), selector=dict(type='pie'))

# --- Gráfico 4: Barras horizontais de CPU ---
cores_cpu = ['#00CC96' if cpu < 50 else '#FFA15A' if cpu < 70 else '#EF553B'
             for cpu in cpu_percent]

fig.add_trace(
    go.Bar(
        x=cpu_percent,
        y=dispositivos,
        orientation='h',
        marker=dict(color=cores_cpu),
        text=[f'{cpu}%' for cpu in cpu_percent],
        textposition='outside',
        showlegend=False
    ),
    row=2, col=2
)

# --- Ajuste de eixos ---
fig.update_xaxes(title_text="Hora", row=1, col=1)
fig.update_yaxes(title_text="Mbps", range=[0, 260], row=1, col=1)

fig.update_xaxes(title_text="Switches", row=1, col=2)
fig.update_yaxes(title_text="Interfaces", range=[0, 60], row=1, col=2)

fig.update_xaxes(title_text="CPU (%)", range=[0, 100], row=2, col=2)
fig.update_yaxes(title_text="", row=2, col=2)

# --- Layout ---
fig.update_layout(
    title_text='🌐 Dashboard de Monitoramento de Rede - MVP',
    title_x=0.5,
    title_font=dict(size=26, color='#2C3E50'),
    showlegend=True,
    height=950,
    plot_bgcolor='#F8F9FA',
    paper_bgcolor='white',
    font=dict(family="Arial", size=12),
    barmode='group',
    annotations=[
        dict(
            text=f'Atualizado em: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}',
            xref='paper', yref='paper',
            x=0.5, y=-0.05,
            xanchor='center', yanchor='top',
            showarrow=False,
            font=dict(size=11, color='#7F8C8D')
        )
    ]
)

# --- Exportar HTML ---
fig.write_html('../../docs/04_dashboard_mvp.html')
print("✅ Dashboard salvo em: 04_dashboard_mvp.html")
print(f"📊 Total de dispositivos: {sum(num_dispositivos)}")
print(f"🔌 Total de interfaces: {sum(interfaces_up) + sum(interfaces_down)}")
print(f"⚠️ Dispositivos críticos: {sum(1 for cpu in cpu_percent if cpu > 70)}")
