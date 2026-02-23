#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard de Progresso CCNP v2 - Métricas por Acumulação

Lê data/ccnp_progress.json e gera dashboard HTML interativo
mostrando conteúdo acumulado por domínio (teoria, labs, resumo).
Abordagem por acumulação: mede o que foi construído, não % de um total desconhecido.

Autor: Alexandre Lavorenti Cancilieri
Data: 2026-02-23
"""

import os
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ============================================================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================================================

BASE_DIR       = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CAMINHO_JSON   = os.path.join(BASE_DIR, 'data', 'ccnp_progress.json')
CAMINHO_OUTPUT = os.path.join(BASE_DIR, 'docs', '12_dashboard_progress.html')

CORES = {
    'teoria': '#636EFA',
    'labs':   '#00CC96',
    'resumo': '#FFA15A',
    'fundo':  '#0F1117',
    'card':   '#1A1D2E',
    'texto':  '#E8EAF6',
}

# ============================================================================
# LEITURA E CÁLCULO DE MÉTRICAS
# ============================================================================

def carregar_dados(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)


def calcular_metricas_dominio(dominio):
    topicos      = dominio.get('topicos', [])
    teoria_ok    = labs_ok = resumo_ok = 0

    for topico in topicos:
        teoria_ok += topico.get('teoria', {}).get('concluidos', 0)
        labs_ok   += topico.get('labs',   {}).get('concluidos', 0)
        resumo_ok += topico.get('resumo', {}).get('concluidos', 0)

    return {
        'id':       dominio['id'],
        'nome':     dominio['nome'],
        'teoria_ok': teoria_ok,
        'labs_ok':   labs_ok,
        'resumo_ok': resumo_ok,
        'iniciado':  (teoria_ok + labs_ok + resumo_ok) > 0,
    }


def calcular_metricas_gerais(dados):
    dominios_metricas = [calcular_metricas_dominio(d) for d in dados['dominios']]

    teoria_ok  = sum(d['teoria_ok']  for d in dominios_metricas)
    labs_ok    = sum(d['labs_ok']    for d in dominios_metricas)
    resumo_ok  = sum(d['resumo_ok']  for d in dominios_metricas)
    concluidos = teoria_ok + labs_ok + resumo_ok

    meta           = datetime.strptime(dados['meta_conclusao'], '%Y-%m-%d')
    dias_restantes = (meta - datetime.now()).days

    return {
        'repositorio':    dados['repositorio'],
        'ultima_att':     dados['ultima_atualizacao'],
        'meta_conclusao': dados['meta_conclusao'],
        'dias_restantes': dias_restantes,
        'teoria_ok':      teoria_ok,
        'labs_ok':        labs_ok,
        'resumo_ok':      resumo_ok,
        'concluidos':     concluidos,
        'dominios':       dominios_metricas,
    }

# ============================================================================
# PREPARAR DADOS PARA OS GRÁFICOS
# ============================================================================

def preparar_dados(metricas):
    dominios  = []
    teoria    = []
    labs      = []
    resumo    = []
    totais    = []
    iniciados = []

    for d in metricas['dominios']:
        dominios.append(d['nome'])
        t = d['teoria_ok']
        l = d['labs_ok']
        r = d['resumo_ok']
        teoria.append(t)
        labs.append(l)
        resumo.append(r)
        totais.append(t + l + r)
        iniciados.append(d['iniciado'])

    return dominios, teoria, labs, resumo, totais, iniciados

# ============================================================================
# GERAR DASHBOARD
# ============================================================================

def gerar_dashboard(metricas):
    dominios, teoria, labs, resumo, totais, iniciados = preparar_dados(metricas)
    g = metricas

    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=(
            '📚 Conteúdo Acumulado por Domínio',
            '🔬 Labs Realizados por Domínio',
            '📊 Distribuição por Tipo',
            '📦 Total Acumulado por Domínio',
            '🎯 Comparativo Teoria vs Labs',
            '📋 Resumo por Domínio',
        ),
        specs=[
            [{'type': 'bar'},  {'type': 'bar'},  {'type': 'pie'}  ],
            [{'type': 'bar'},  {'type': 'bar'},  {'type': 'table'}],
        ],
        vertical_spacing=0.18,
        horizontal_spacing=0.10,
    )

    # [1,1] Barras empilhadas
    fig.add_trace(go.Bar(name='Teoria', x=dominios, y=teoria,
        marker_color=CORES['teoria'], text=teoria, textposition='inside',
        hovertemplate='<b>%{x}</b><br>Teoria: %{y} aulas<extra></extra>',
    ), row=1, col=1)

    fig.add_trace(go.Bar(name='Labs', x=dominios, y=labs,
        marker_color=CORES['labs'], text=labs, textposition='inside',
        hovertemplate='<b>%{x}</b><br>Labs: %{y}<extra></extra>',
    ), row=1, col=1)

    fig.add_trace(go.Bar(name='Resumo', x=dominios, y=resumo,
        marker_color=CORES['resumo'], text=resumo, textposition='inside',
        hovertemplate='<b>%{x}</b><br>Resumo: %{y}<extra></extra>',
    ), row=1, col=1)

    # [1,2] Labs por domínio
    cores_barras = [CORES['labs'] if i else '#2A2D3E' for i in iniciados]
    fig.add_trace(go.Bar(name='Labs por Domínio', x=dominios, y=labs,
        marker_color=cores_barras, text=labs, textposition='outside',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Labs realizados: %{y}<extra></extra>',
    ), row=1, col=2)

    # [1,3] Donut
    fig.add_trace(go.Pie(
        labels=['Teoria', 'Labs', 'Resumo'],
        values=[g['teoria_ok'], g['labs_ok'], g['resumo_ok']],
        marker_colors=[CORES['teoria'], CORES['labs'], CORES['resumo']],
        hole=0.45, showlegend=False,
        hovertemplate='<b>%{label}</b><br>%{value} itens (%{percent})<extra></extra>',
        textinfo='label+value',
    ), row=1, col=3)

    # [2,1] Total com colorscale
    fig.add_trace(go.Bar(name='Total Acumulado', x=dominios, y=totais,
        marker=dict(
            color=totais,
            colorscale=[[0, '#1A1D2E'], [0.3, '#636EFA'], [1, '#00CC96']],
            showscale=False,
        ),
        text=totais, textposition='outside', showlegend=False,
        hovertemplate='<b>%{x}</b><br>Total acumulado: %{y} itens<extra></extra>',
    ), row=2, col=1)

    # [2,2] Comparativo teoria vs labs
    fig.add_trace(go.Bar(name='Teoria ', x=dominios, y=teoria,
        marker_color=CORES['teoria'], showlegend=False,
        hovertemplate='<b>%{x}</b><br>Teoria: %{y}<extra></extra>',
    ), row=2, col=2)

    fig.add_trace(go.Bar(name='Labs ', x=dominios, y=labs,
        marker_color=CORES['labs'], showlegend=False,
        hovertemplate='<b>%{x}</b><br>Labs: %{y}<extra></extra>',
    ), row=2, col=2)

    # [2,3] Tabela
    fig.add_trace(go.Table(
        header=dict(
            values=['<b>Domínio</b>', '<b>Teoria</b>', '<b>Labs</b>',
                    '<b>Resumo</b>', '<b>Total</b>', '<b>Status</b>'],
            fill_color='#2A2D3E',
            font=dict(color=CORES['texto'], size=11),
            align='center', height=28,
        ),
        cells=dict(
            values=[
                [d['nome']      for d in metricas['dominios']],
                [d['teoria_ok'] for d in metricas['dominios']],
                [d['labs_ok']   for d in metricas['dominios']],
                [d['resumo_ok'] for d in metricas['dominios']],
                [d['teoria_ok'] + d['labs_ok'] + d['resumo_ok'] for d in metricas['dominios']],
                ['✅' if d['iniciado'] else '⬜' for d in metricas['dominios']],
            ],
            fill_color=[['#1A1D2E', '#151821'] * 3],
            font=dict(color=CORES['texto'], size=11),
            align=['left', 'center', 'center', 'center', 'center', 'center'],
            height=25,
        ),
    ), row=2, col=3)

    # Layout
    fig.update_layout(
        title=dict(
            text=(
                f'📊 CCNP 350-401 ENCOR — Dashboard de Progresso<br>'
                f'<sub>Conteúdo acumulado por domínio  •  '
                f'Atualizado em {g["ultima_att"]}  •  '
                f'{g["dias_restantes"]} dias até a meta</sub>'
            ),
            x=0.5, xanchor='center',
            font=dict(size=18, color=CORES['texto']),
        ),
        height=820,
        paper_bgcolor=CORES['fundo'],
        plot_bgcolor='#151821',
        font=dict(family='Courier New, monospace', size=11, color=CORES['texto']),
        barmode='stack',
        legend=dict(orientation='h', y=1.06, x=0.5, xanchor='center',
                    font=dict(size=11), bgcolor='rgba(0,0,0,0)'),
        margin=dict(t=120, b=40, l=40, r=40),
        hoverlabel=dict(bgcolor='#2A2D3E', font=dict(color=CORES['texto'])),
    )

    fig.update_xaxes(tickfont=dict(size=9), gridcolor='#2A2D3E', tickangle=-15)
    fig.update_yaxes(gridcolor='#2A2D3E', zerolinecolor='#2A2D3E')

    for texto, xpos, cor, borda in [
        (f'📚 {g["teoria_ok"]} aulas',   0.08, CORES['teoria'], CORES['teoria']),
        (f'🔬 {g["labs_ok"]} labs',       0.22, CORES['labs'],   CORES['labs']),
        (f'📝 {g["resumo_ok"]} resumos',  0.38, CORES['resumo'], CORES['resumo']),
        (f'📦 {g["concluidos"]} total',   0.54, CORES['texto'],  '#3A3D4E'),
    ]:
        fig.add_annotation(
            text=texto, x=xpos, y=1.12, xref='paper', yref='paper',
            showarrow=False, font=dict(size=13, color=cor),
            bgcolor='#1A1D2E', bordercolor=borda, borderwidth=1, borderpad=6,
        )

    return fig

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == '__main__':
    dados    = carregar_dados(CAMINHO_JSON)
    metricas = calcular_metricas_gerais(dados)
    fig      = gerar_dashboard(metricas)
    fig.write_html(CAMINHO_OUTPUT)
    print(f'✅ Dashboard salvo em: docs/12_dashboard_progress.html')
    print(f'\n📊 Resumo:')
    print(f'  📚 Teoria  : {metricas["teoria_ok"]} aulas')
    print(f'  🔬 Labs    : {metricas["labs_ok"]} realizados')
    print(f'  📝 Resumo  : {metricas["resumo_ok"]} concluídos')
    print(f'  📦 Total   : {metricas["concluidos"]} itens acumulados')