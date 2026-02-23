#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leitura e Métricas do Progresso CCNP

Lê o arquivo data/ccnp_progress.json, calcula métricas por domínio
e exibe resumo no terminal. Serve como módulo base para os dashboards.

Autor: Alexandre Lavorenti Cancilieri
Data: 2026-02-22
"""

import json
import os
from datetime import datetime

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

CAMINHO_JSON = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'ccnp_progress.json')

# ============================================================================
# FUNÇÕES DE LEITURA
# ============================================================================

def carregar_dados(caminho=CAMINHO_JSON):
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)


def calcular_metricas_topico(topico):
    teoria     = topico.get('teoria', {})
    labs       = topico.get('labs',   {})
    resumo     = topico.get('resumo', {})

    total      = teoria.get('total', 0) + labs.get('total', 0) + resumo.get('total', 0)
    concluidos = teoria.get('concluidos', 0) + labs.get('concluidos', 0) + resumo.get('concluidos', 0)
    percentual = round((concluidos / total * 100), 1) if total > 0 else 0.0

    return {
        'nome':            topico['nome'],
        'teoria_total':    teoria.get('total', 0),
        'teoria_ok':       teoria.get('concluidos', 0),
        'labs_total':      labs.get('total', 0),
        'labs_ok':         labs.get('concluidos', 0),
        'resumo_total':    resumo.get('total', 0),
        'resumo_ok':       resumo.get('concluidos', 0),
        'total':           total,
        'concluidos':      concluidos,
        'percentual':      percentual,
    }


def calcular_metricas_dominio(dominio):
    topicos = dominio.get('topicos', [])

    teoria_total = labs_total = resumo_total = 0
    teoria_ok    = labs_ok    = resumo_ok    = 0

    metricas_topicos = []
    for topico in topicos:
        m = calcular_metricas_topico(topico)
        metricas_topicos.append(m)
        teoria_total += m['teoria_total'];  teoria_ok += m['teoria_ok']
        labs_total   += m['labs_total'];    labs_ok   += m['labs_ok']
        resumo_total += m['resumo_total'];  resumo_ok += m['resumo_ok']

    total      = teoria_total + labs_total + resumo_total
    concluidos = teoria_ok    + labs_ok    + resumo_ok
    percentual = round((concluidos / total * 100), 1) if total > 0 else 0.0

    return {
        'id':             dominio['id'],
        'nome':           dominio['nome'],
        'teoria_total':   teoria_total,
        'teoria_ok':      teoria_ok,
        'labs_total':     labs_total,
        'labs_ok':        labs_ok,
        'resumo_total':   resumo_total,
        'resumo_ok':      resumo_ok,
        'total':          total,
        'concluidos':     concluidos,
        'percentual':     percentual,
        'topicos':        metricas_topicos,
        'iniciado':       total > 0,
    }


def calcular_metricas_gerais(dados):
    dominios_metricas = [calcular_metricas_dominio(d) for d in dados['dominios']]

    teoria_total = sum(d['teoria_total'] for d in dominios_metricas)
    teoria_ok    = sum(d['teoria_ok']    for d in dominios_metricas)
    labs_total   = sum(d['labs_total']   for d in dominios_metricas)
    labs_ok      = sum(d['labs_ok']      for d in dominios_metricas)
    resumo_total = sum(d['resumo_total'] for d in dominios_metricas)
    resumo_ok    = sum(d['resumo_ok']    for d in dominios_metricas)

    total      = teoria_total + labs_total + resumo_total
    concluidos = teoria_ok    + labs_ok    + resumo_ok
    percentual = round((concluidos / total * 100), 1) if total > 0 else 0.0

    ultima_att  = datetime.strptime(dados['ultima_atualizacao'], '%Y-%m-%d')
    meta        = datetime.strptime(dados['meta_conclusao'],     '%Y-%m-%d')
    hoje        = datetime.now()
    dias_restantes = (meta - hoje).days

    return {
        'repositorio':     dados['repositorio'],
        'ultima_att':      dados['ultima_atualizacao'],
        'meta_conclusao':  dados['meta_conclusao'],
        'dias_restantes':  dias_restantes,
        'teoria_total':    teoria_total,
        'teoria_ok':       teoria_ok,
        'labs_total':      labs_total,
        'labs_ok':         labs_ok,
        'resumo_total':    resumo_total,
        'resumo_ok':       resumo_ok,
        'total':           total,
        'concluidos':      concluidos,
        'percentual':      percentual,
        'dominios':        dominios_metricas,
    }

# ============================================================================
# EXIBIÇÃO NO TERMINAL
# ============================================================================

def exibir_resumo(metricas):
    g = metricas
    print("=" * 55)
    print(f"  📚 {g['repositorio']}")
    print(f"  📅 Atualizado : {g['ultima_att']}")
    print(f"  🎯 Meta       : {g['meta_conclusao']} ({g['dias_restantes']} dias restantes)")
    print("=" * 55)

    for d in g['dominios']:
        if not d['iniciado']:
            print(f"\n⬜ {d['id']} - {d['nome']}  (não iniciado)")
            continue

        barra = gerar_barra(d['percentual'])
        print(f"\n🟢 {d['id']} - {d['nome']}")
        print(f"   {barra}  {d['percentual']}%")
        print(f"   Teoria  : {d['teoria_ok']}/{d['teoria_total']}")
        print(f"   Labs    : {d['labs_ok']}/{d['labs_total']}")
        print(f"   Resumo  : {d['resumo_ok']}/{d['resumo_total']}")

    print("\n" + "=" * 55)
    barra_geral = gerar_barra(g['percentual'])
    print(f"  PROGRESSO GERAL  {barra_geral}  {g['percentual']}%")
    print(f"  Itens concluídos : {g['concluidos']}/{g['total']}")
    print(f"  Teoria  : {g['teoria_ok']}/{g['teoria_total']}")
    print(f"  Labs    : {g['labs_ok']}/{g['labs_total']}")
    print(f"  Resumo  : {g['resumo_ok']}/{g['resumo_total']}")
    print("=" * 55)


def gerar_barra(percentual, tamanho=20):
    preenchido = int(percentual / 100 * tamanho)
    return '[' + '█' * preenchido + '░' * (tamanho - preenchido) + ']'

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == '__main__':
    dados    = carregar_dados()
    metricas = calcular_metricas_gerais(dados)
    exibir_resumo(metricas)