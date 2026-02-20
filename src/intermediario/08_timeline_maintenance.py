#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico Timeline - Janelas de Manutenção

Visualiza planejamento de manutenções preventivas em dispositivos de rede.
Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-20
"""

import plotly.figure_factory as ff
from datetime import datetime, timedelta
import random

# Seed para reprodutibilidade
random.seed(42)

# Tipos de manutenção e suas cores
tipos_manutencao = {
    'Upgrade Firmware': '#3498db',      # Azul
    'Backup Config': '#2ecc71',         # Verde
    'Análise Performance': '#f39c12',   # Laranja
    'Manutenção Preventiva': '#9b59b6', # Roxo
    'Substituição HW': '#e74c3c'        # Vermelho
}

# Dispositivos a serem mantidos
dispositivos = [
    'RTR-CORE-01', 'RTR-EDGE-01', 'SW-CORE-01', 
    'SW-DIST-01', 'SW-DIST-02', 'SW-ACCESS-01',
    'FW-01', 'FW-02', 'LB-01', 'LB-02'
]

# Gerar janelas de manutenção
manutencoes = []
data_inicio = datetime.now()

for i, dispositivo in enumerate(dispositivos):
    # Cada dispositivo tem 2-3 manutenções nos próximos 90 dias
    num_manutencoes = random.randint(2, 3)
    
    for j in range(num_manutencoes):
        # Data aleatória nos próximos 90 dias
        dias_offset = random.randint(i*7, 90)
        inicio = data_inicio + timedelta(days=dias_offset)
        
        # Duração: 2-8 horas
        duracao_horas = random.randint(2, 8)
        fim = inicio + timedelta(hours=duracao_horas)
        
        # Tipo de manutenção aleatório
        tipo = random.choice(list(tipos_manutencao.keys()))
        
        manutencoes.append(dict(
            Task=dispositivo,
            Start=inicio,
            Finish=fim,
            Resource=tipo,
            Description=f'{tipo} - {duracao_horas}h'
        ))

# Criar timeline (Gantt chart)
fig = ff.create_gantt(
    manutencoes,
    colors=tipos_manutencao,
    index_col='Resource',
    show_colorbar=True,
    group_tasks=True,
    showgrid_x=True,
    showgrid_y=True,
    title='📅 Cronograma de Manutenções - Próximos 90 Dias',
    bar_width=0.3,
    height=600
)

# Customizar layout
fig.update_layout(
    xaxis=dict(
        title='Data',
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True
    ),
    yaxis=dict(
        title='Dispositivos',
        gridcolor='rgba(128,128,128,0.2)',
        showgrid=True
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family='Arial', size=12),
    hovermode='closest'
)

# Customizar hover
fig.update_traces(
    hovertemplate='<b>%{y}</b><br>' +
                  'Início: %{base|%d/%m %H:%M}<br>' +
                  'Fim: %{x|%d/%m %H:%M}<br>' +
                  '<extra></extra>'
)

# Exportar
fig.write_html('../../docs/08_timeline_maintenance.html')
print("✅ Timeline salvo em: docs/08_timeline_maintenance.html")
print(f"\n📊 Resumo do Planejamento:")
print(f"📅 Período: {data_inicio.strftime('%d/%m/%Y')} a {(data_inicio + timedelta(days=90)).strftime('%d/%m/%Y')}")
print(f"🔧 Total de manutenções: {len(manutencoes)}")
print(f"🖥️  Dispositivos: {len(dispositivos)}")
print(f"\n📋 Por tipo:")
for tipo in tipos_manutencao.keys():
    count = sum(1 for m in manutencoes if m['Resource'] == tipo)
    print(f"  {tipo}: {count}")