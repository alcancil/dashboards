#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard de Progresso CCNP v2 - Métricas por Acumulação (VERSÃO DIDÁTICA)

Lê data/ccnp_progress.json e gera dashboard HTML interativo
mostrando conteúdo acumulado por domínio (teoria, labs, resumo).

DIFERENÇA EM RELAÇÃO AO SCRIPT 11:
- Script 11 (v1): usava total/concluidos → mostrava % de um plano fixo
- Script 12 (v2): usa apenas concluidos  → mede o que foi construído
- Abordagem v2 é ideal para repositórios em construção contínua onde
  não se sabe antecipadamente quantos itens serão criados

POR QUE NÃO USAMOS HELPER EXTERNO:
- Python instalado via Microsoft Store tem sandboxing que impede
  sys.path.insert de funcionar corretamente para importar módulos locais
- Solução: script autossuficiente com todas as funções embutidas
- Vantagem extra: script funciona em qualquer ambiente sem configuração

Autor: Alexandre Lavorenti Cancilieri
Data: 2026-02-23
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import os            # Manipulação de caminhos de arquivos e pastas
import json          # Leitura do arquivo ccnp_progress.json
import plotly.graph_objects as go          # Tipos de trace: Bar, Pie, Table
from plotly.subplots import make_subplots  # Grade de subplots
from datetime import datetime              # Cálculo de dias restantes até a meta

# ============================================================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================================================

# os.path.abspath() → converte para caminho absoluto (evita problemas de path relativo)
# os.path.dirname(__file__) → pasta onde este script está: src/avancado/
# '..', '..' → sobe duas pastas: avancado → src → dashboards (raiz)
# Resultado: D:\Estudos\Phyton\dashboards
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Caminho completo até o arquivo de dados
# BASE_DIR + 'data' + 'ccnp_progress.json'
CAMINHO_JSON = os.path.join(BASE_DIR, 'data', 'ccnp_progress.json')

# Caminho completo do arquivo HTML de saída
# BASE_DIR + 'docs' + '12_dashboard_progress.html'
CAMINHO_OUTPUT = os.path.join(BASE_DIR, 'docs', '12_dashboard_progress.html')

# ============================================================================
# PALETA DE CORES
# ============================================================================

# Tema escuro estilo terminal — coerente com o contexto de redes e automação
# Dicionário com nomes semânticos para facilitar manutenção
CORES = {
    'teoria': '#636EFA',   # Azul    → aulas teóricas
    'labs':   '#00CC96',   # Verde   → laboratórios práticos
    'resumo': '#FFA15A',   # Laranja → resumos e revisões
    'fundo':  '#0F1117',   # Preto-azulado → fundo geral da figura
    'card':   '#1A1D2E',   # Cinza-escuro  → fundo dos cards e tabela
    'texto':  '#E8EAF6',   # Branco-suave  → texto em geral
}

# ============================================================================
# LEITURA DO JSON
# ============================================================================

def carregar_dados(caminho):
    """
    Abre o arquivo JSON e retorna o conteúdo como dicionário Python.
    encoding='utf-8' garante que caracteres especiais (ã, ç, etc.) sejam lidos corretamente.
    """
    with open(caminho, 'r', encoding='utf-8') as f:   # Abre em modo leitura ('r')
        return json.load(f)                            # Converte JSON → dicionário Python

# ============================================================================
# CÁLCULO DE MÉTRICAS POR DOMÍNIO
# ============================================================================

def calcular_metricas_dominio(dominio):
    """
    Recebe um dicionário de domínio do JSON e retorna métricas de acumulação.

    DIFERENÇA DA ABORDAGEM v2:
    - v1 (script 11): somava 'total' e 'concluidos' → calculava percentual
    - v2 (script 12): soma apenas 'concluidos' de cada tipo → valor absoluto acumulado
    - Não há divisão, não há percentual — só contagem do que foi feito
    """

    topicos   = dominio.get('topicos', [])   # Lista de tópicos do domínio
                                             # .get() com padrão [] evita KeyError

    # Contadores zerados — acumulam os valores de todos os tópicos do domínio
    teoria_ok = 0   # Total de aulas de teoria concluídas no domínio
    labs_ok   = 0   # Total de labs concluídos no domínio
    resumo_ok = 0   # Total de resumos concluídos no domínio

    for topico in topicos:                                           # Itera sobre cada tópico
        teoria_ok += topico.get('teoria', {}).get('concluidos', 0)  # Soma teoria deste tópico
        labs_ok   += topico.get('labs',   {}).get('concluidos', 0)  # Soma labs deste tópico
        resumo_ok += topico.get('resumo', {}).get('concluidos', 0)  # Soma resumo deste tópico
        # .get('teoria', {}) → se não tiver chave 'teoria', retorna dict vazio
        # .get('concluidos', 0) → se não tiver 'concluidos', retorna 0
        # Duas chamadas .get() encadeadas evitam KeyError em qualquer nível

    return {
        'id':        dominio['id'],    # Ex: '01', '02', etc.
        'nome':      dominio['nome'],  # Ex: 'Architecture'
        'teoria_ok': teoria_ok,        # Aulas concluídas no domínio
        'labs_ok':   labs_ok,          # Labs concluídos no domínio
        'resumo_ok': resumo_ok,        # Resumos concluídos no domínio
        'iniciado':  (teoria_ok + labs_ok + resumo_ok) > 0,
        # iniciado = True se o domínio tem pelo menos 1 item concluído
        # Usado para colorir barras: verde (iniciado) ou cinza (não iniciado)
    }

# ============================================================================
# CÁLCULO DE MÉTRICAS GERAIS
# ============================================================================

def calcular_metricas_gerais(dados):
    """
    Consolida métricas de todos os domínios e calcula totais gerais.
    Recebe o dicionário completo do JSON e retorna o dicionário de métricas
    que o dashboard vai consumir.
    """

    # List comprehension: calcula métricas de todos os domínios de uma vez
    # Equivale a: metricas = []; for d in dados['dominios']: metricas.append(calcular...)
    dominios_metricas = [calcular_metricas_dominio(d) for d in dados['dominios']]

    # sum() com generator expression: soma um campo específico de cada domínio
    # Equivale a: total = 0; for d in dominios_metricas: total += d['teoria_ok']
    teoria_ok  = sum(d['teoria_ok']  for d in dominios_metricas)   # Total geral de teoria
    labs_ok    = sum(d['labs_ok']    for d in dominios_metricas)   # Total geral de labs
    resumo_ok  = sum(d['resumo_ok']  for d in dominios_metricas)   # Total geral de resumo
    concluidos = teoria_ok + labs_ok + resumo_ok                   # Grand total

    # Calcular dias restantes até a meta de conclusão
    meta           = datetime.strptime(dados['meta_conclusao'], '%Y-%m-%d')
    # datetime.strptime() → converte string '2027-12-31' para objeto datetime
    # '%Y-%m-%d' → formato esperado: ano-mês-dia
    dias_restantes = (meta - datetime.now()).days
    # Subtração de dois objetos datetime → timedelta
    # .days → extrai apenas os dias inteiros do timedelta

    return {
        'repositorio':    dados['repositorio'],        # Nome do repositório
        'ultima_att':     dados['ultima_atualizacao'], # Data da última atualização
        'meta_conclusao': dados['meta_conclusao'],     # Data meta de conclusão
        'dias_restantes': dias_restantes,              # Dias restantes até a meta
        'teoria_ok':      teoria_ok,                   # Total geral de teoria
        'labs_ok':        labs_ok,                     # Total geral de labs
        'resumo_ok':      resumo_ok,                   # Total geral de resumo
        'concluidos':     concluidos,                  # Grand total de itens
        'dominios':       dominios_metricas,           # Lista com métricas por domínio
    }

# ============================================================================
# PREPARAR LISTAS PARALELAS PARA OS GRÁFICOS
# ============================================================================

def preparar_dados(metricas):
    """
    Extrai valores do dicionário de métricas e organiza em listas paralelas.
    Listas paralelas = uma posição por domínio, na mesma ordem.
    Esse é o formato que o Plotly espera para traces de barra.

    Ex: dominios[0]='Architecture', teoria[0]=31, labs[0]=5, totais[0]=37
    """

    dominios  = []   # Nomes dos domínios (eixo X dos gráficos de barra)
    teoria    = []   # Aulas de teoria por domínio
    labs      = []   # Labs por domínio
    resumo    = []   # Resumos por domínio
    totais    = []   # Soma teoria+labs+resumo por domínio
    iniciados = []   # True/False: domínio tem pelo menos 1 item

    for d in metricas['dominios']:      # Itera sobre os 6 domínios
        dominios.append(d['nome'])      # Ex: 'Architecture'
        t = d['teoria_ok']              # Atalho para não repetir d['teoria_ok']
        l = d['labs_ok']                # Atalho para labs
        r = d['resumo_ok']              # Atalho para resumo
        teoria.append(t)                # Adiciona à lista de teoria
        labs.append(l)                  # Adiciona à lista de labs
        resumo.append(r)                # Adiciona à lista de resumo
        totais.append(t + l + r)        # Total acumulado do domínio
        iniciados.append(d['iniciado']) # True se t+l+r > 0

    return dominios, teoria, labs, resumo, totais, iniciados   # 6 listas paralelas

# ============================================================================
# GERAR DASHBOARD
# ============================================================================

def gerar_dashboard(metricas):
    """
    Cria a figura Plotly com 6 subplots em grade 2x3 e retorna o objeto fig.
    """

    # Desempacotar as 6 listas retornadas por preparar_dados
    dominios, teoria, labs, resumo, totais, iniciados = preparar_dados(metricas)
    g = metricas   # Atalho para não repetir 'metricas.' em todo lugar

    # ---- Criar grade de subplots 2x3 ----
    fig = make_subplots(
        rows=2, cols=3,   # 2 linhas × 3 colunas = 6 subplots

        subplot_titles=(                              # Títulos de cada subplot
            '📚 Conteúdo Acumulado por Domínio',      # Subplot [1,1]
            '🔬 Labs Realizados por Domínio',          # Subplot [1,2]
            '📊 Distribuição por Tipo',                # Subplot [1,3]
            '📦 Total Acumulado por Domínio',          # Subplot [2,1]
            '🎯 Comparativo Teoria vs Labs',           # Subplot [2,2]
            '📋 Resumo por Domínio',                   # Subplot [2,3]
        ),

        specs=[                                        # Tipos de cada subplot
            [{'type': 'bar'},  {'type': 'bar'},  {'type': 'pie'}  ],   # linha 1
            [{'type': 'bar'},  {'type': 'bar'},  {'type': 'table'}],   # linha 2
        ],
        # 'pie' e 'table' precisam ser declarados em specs
        # pois não são tipos cartesianos (não usam eixos X/Y tradicionais)

        vertical_spacing=0.18,    # 18% de espaço vertical entre as linhas
        horizontal_spacing=0.10,  # 10% de espaço horizontal entre as colunas
    )

    # ========================================================================
    # SUBPLOT [1,1]: Barras empilhadas — conteúdo acumulado por domínio
    # ========================================================================
    # barmode='stack' no layout vai empilhar os 3 traces verticalmente
    # Ordem de empilhamento = ordem de add_trace: teoria (baixo) → labs → resumo (topo)

    fig.add_trace(go.Bar(
        name='Teoria',                 # Nome na legenda global
        x=dominios,                    # Eixo X: nomes dos 6 domínios
        y=teoria,                      # Eixo Y: quantidade de aulas de teoria
        marker_color=CORES['teoria'],  # Cor azul definida no dicionário CORES
        text=teoria,                   # Valor exibido dentro de cada segmento
        textposition='inside',         # Texto dentro da barra (não flutua fora)
        hovertemplate='<b>%{x}</b><br>Teoria: %{y} aulas<extra></extra>',
        # %{x} = nome do domínio, %{y} = valor, <extra></extra> = remove caixinha lateral
    ), row=1, col=1)   # Posicionar no subplot superior esquerdo

    fig.add_trace(go.Bar(
        name='Labs',
        x=dominios, y=labs,
        marker_color=CORES['labs'],    # Cor verde para labs
        text=labs, textposition='inside',
        hovertemplate='<b>%{x}</b><br>Labs: %{y}<extra></extra>',
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        name='Resumo',
        x=dominios, y=resumo,
        marker_color=CORES['resumo'],  # Cor laranja para resumo
        text=resumo, textposition='inside',
        hovertemplate='<b>%{x}</b><br>Resumo: %{y}<extra></extra>',
    ), row=1, col=1)

    # ========================================================================
    # SUBPLOT [1,2]: Barras simples — labs por domínio com cor condicional
    # ========================================================================
    # List comprehension com operador ternário:
    # Para cada domínio, se iniciado=True → verde, se False → cinza escuro
    # Sintaxe: [valor_se_true if condição else valor_se_false for item in lista]
    cores_barras = [CORES['labs'] if i else '#2A2D3E' for i in iniciados]

    fig.add_trace(go.Bar(
        name='Labs por Domínio',
        x=dominios, y=labs,
        marker_color=cores_barras,     # Lista de cores: uma por domínio
        text=labs,
        textposition='outside',        # Texto acima da barra
        showlegend=False,              # Não duplicar na legenda global
        hovertemplate='<b>%{x}</b><br>Labs realizados: %{y}<extra></extra>',
    ), row=1, col=2)

    # ========================================================================
    # SUBPLOT [1,3]: Donut chart — distribuição por tipo de atividade
    # ========================================================================
    # Mostra proporção global entre teoria, labs e resumo
    # hole=0.45 cria o buraco central → donut chart

    fig.add_trace(go.Pie(
        labels=['Teoria', 'Labs', 'Resumo'],                              # Rótulos das fatias
        values=[g['teoria_ok'], g['labs_ok'], g['resumo_ok']],            # Valores totais globais
        marker_colors=[CORES['teoria'], CORES['labs'], CORES['resumo']],  # Cores por fatia
        hole=0.45,         # 45% de buraco no centro → donut chart
        showlegend=False,  # Não adicionar à legenda global
        hovertemplate='<b>%{label}</b><br>%{value} itens (%{percent})<extra></extra>',
        textinfo='label+value',   # Exibe rótulo + valor em cada fatia
    ), row=1, col=3)

    # ========================================================================
    # SUBPLOT [2,1]: Barras com colorscale — total acumulado por domínio
    # ========================================================================
    # colorscale mapeia o valor numérico para uma cor gradiente
    # [[posição_0_a_1, cor], ...] — quanto maior o total, mais verde

    fig.add_trace(go.Bar(
        name='Total Acumulado',
        x=dominios, y=totais,
        marker=dict(
            color=totais,              # Valores numéricos mapeados no colorscale
            colorscale=[               # Gradiente: cinza escuro → azul → verde
                [0,   '#1A1D2E'],      # 0%   → cinza escuro (domínio vazio)
                [0.3, '#636EFA'],      # 30%  → azul (pouco conteúdo)
                [1,   '#00CC96'],      # 100% → verde (muito conteúdo)
            ],
            showscale=False,           # Não exibir barra de escala lateral
        ),
        text=totais, textposition='outside',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Total acumulado: %{y} itens<extra></extra>',
    ), row=2, col=1)

    # ========================================================================
    # SUBPLOT [2,2]: Barras empilhadas — comparativo teoria vs labs
    # ========================================================================
    # showlegend=False evita duplicar os itens já presentes da legenda do [1,1]
    # name com espaço extra ('Teoria ') evita conflito de nome com trace de [1,1]

    fig.add_trace(go.Bar(
        name='Teoria ',                # Espaço no final diferencia do trace do subplot [1,1]
        x=dominios, y=teoria,
        marker_color=CORES['teoria'],
        showlegend=False,              # Já aparece na legenda via subplot [1,1]
        hovertemplate='<b>%{x}</b><br>Teoria: %{y}<extra></extra>',
    ), row=2, col=2)

    fig.add_trace(go.Bar(
        name='Labs ',                  # Espaço no final diferencia do trace do subplot [1,1]
        x=dominios, y=labs,
        marker_color=CORES['labs'],
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Labs: %{y}<extra></extra>',
    ), row=2, col=2)

    # ========================================================================
    # SUBPLOT [2,3]: Tabela — resumo por domínio
    # ========================================================================

    fig.add_trace(go.Table(
        header=dict(                   # Configuração do cabeçalho
            values=[                   # Lista de strings HTML para cada coluna
                '<b>Domínio</b>', '<b>Teoria</b>', '<b>Labs</b>',
                '<b>Resumo</b>', '<b>Total</b>', '<b>Status</b>',
            ],
            fill_color='#2A2D3E',      # Fundo do cabeçalho
            font=dict(color=CORES['texto'], size=11),
            align='center',
            height=28,                 # Altura do cabeçalho em pixels
        ),
        cells=dict(                    # Configuração das células de dados
            values=[                   # Uma lista por coluna (não por linha)
                [d['nome']      for d in metricas['dominios']],   # Coluna Domínio
                [d['teoria_ok'] for d in metricas['dominios']],   # Coluna Teoria
                [d['labs_ok']   for d in metricas['dominios']],   # Coluna Labs
                [d['resumo_ok'] for d in metricas['dominios']],   # Coluna Resumo
                [d['teoria_ok'] + d['labs_ok'] + d['resumo_ok']   # Coluna Total
                 for d in metricas['dominios']],
                ['✅' if d['iniciado'] else '⬜'                    # Coluna Status
                 for d in metricas['dominios']],
            ],
            fill_color=[['#1A1D2E', '#151821'] * 3],
            # Zebra striping: alterna entre dois tons de cinza escuro
            # ['cor1', 'cor2'] * 3 = ['cor1','cor2','cor1','cor2','cor1','cor2']
            # Cobre as 6 linhas (um por domínio)
            font=dict(color=CORES['texto'], size=11),
            align=['left', 'center', 'center', 'center', 'center', 'center'],
            # 'left' para o nome do domínio, 'center' para os valores numéricos
            height=25,                 # Altura de cada linha em pixels
        ),
    ), row=2, col=3)

    # ========================================================================
    # LAYOUT GLOBAL
    # ========================================================================

    fig.update_layout(
        title=dict(
            text=(
                f'📊 CCNP 350-401 ENCOR — Dashboard de Progresso<br>'
                f'<sub>Conteúdo acumulado por domínio  •  '
                f'Atualizado em {g["ultima_att"]}  •  '
                f'{g["dias_restantes"]} dias até a meta</sub>'
                # f-string: insere os valores do JSON diretamente no título
                # <sub>...</sub> = subtítulo em fonte menor
            ),
            x=0.5, xanchor='center',            # Título centralizado horizontalmente
            font=dict(size=18, color=CORES['texto']),
        ),

        height=820,                             # Altura total da figura em pixels

        paper_bgcolor=CORES['fundo'],           # Fundo externo: preto-azulado (#0F1117)
        plot_bgcolor='#151821',                 # Fundo interno dos subplots

        font=dict(
            family='Courier New, monospace',    # Fonte monoespaçada: remete a terminal/código
            size=11,
            color=CORES['texto'],
        ),

        barmode='stack',                        # Barras empilhadas em todos os subplots de barra

        legend=dict(
            orientation='h',                    # Legenda horizontal
            y=1.06,                             # 6% acima do topo da área de plotagem
            x=0.5, xanchor='center',
            font=dict(size=11),
            bgcolor='rgba(0,0,0,0)',            # Fundo transparente
        ),

        margin=dict(t=120, b=40, l=40, r=40),  # t=120: espaço para os cards no topo

        hoverlabel=dict(
            bgcolor='#2A2D3E',                  # Fundo do tooltip
            font=dict(color=CORES['texto']),
        ),
    )

    fig.update_xaxes(
        tickfont=dict(size=9),    # Fonte pequena nos rótulos do eixo X
        gridcolor='#2A2D3E',      # Grade cinza escuro discreto
        tickangle=-15,            # Rótulos levemente inclinados
    )
    fig.update_yaxes(
        gridcolor='#2A2D3E',      # Grade Y: mesma cor
        zerolinecolor='#2A2D3E', # Linha do zero: mesma cor da grade
    )

    # ========================================================================
    # CARDS DE TOTAIS NO TOPO (annotations)
    # ========================================================================
    # Annotations são textos flutuantes em coordenadas 'paper' (0 a 1)
    # y=1.12 → 12% acima do topo da área de plotagem
    # Loop sobre lista de tuplas evita repetir fig.add_annotation 4 vezes

    for texto, xpos, cor, borda in [
        (f'📚 {g["teoria_ok"]} aulas',   0.08, CORES['teoria'], CORES['teoria']),
        (f'🔬 {g["labs_ok"]} labs',       0.22, CORES['labs'],   CORES['labs']),
        (f'📝 {g["resumo_ok"]} resumos',  0.38, CORES['resumo'], CORES['resumo']),
        (f'📦 {g["concluidos"]} total',   0.54, CORES['texto'],  '#3A3D4E'),
    ]:
        fig.add_annotation(
            text=texto,                    # Texto exibido no card
            x=xpos, y=1.12,               # Posição acima do topo
            xref='paper', yref='paper',   # Coordenadas relativas à figura (0-1)
            showarrow=False,              # Sem seta
            font=dict(size=13, color=cor),
            bgcolor='#1A1D2E',            # Fundo do card
            bordercolor=borda,            # Borda colorida por tipo
            borderwidth=1,
            borderpad=6,                  # Padding interno em pixels
        )

    return fig   # Retorna o objeto figura para ser salvo em HTML

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == '__main__':
    dados    = carregar_dados(CAMINHO_JSON)      # 1. Lê o JSON
    metricas = calcular_metricas_gerais(dados)   # 2. Calcula métricas
    fig      = gerar_dashboard(metricas)         # 3. Gera o dashboard
    fig.write_html(CAMINHO_OUTPUT)               # 4. Salva como HTML interativo

    print(f'✅ Dashboard salvo em: docs/12_dashboard_progress.html')
    print(f'\n📊 Resumo:')
    print(f'  📚 Teoria  : {metricas["teoria_ok"]} aulas')
    print(f'  🔬 Labs    : {metricas["labs_ok"]} realizados')
    print(f'  📝 Resumo  : {metricas["resumo_ok"]} concluídos')
    print(f'  📦 Total   : {metricas["concluidos"]} itens acumulados')

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Certifique-se que o arquivo de dados existe:
   dashboards/data/ccnp_progress.json

2. Execute o script de qualquer pasta:
   python src/avancado/12_dashboard_progress_commented.py

3. Abra o arquivo gerado no navegador:
   docs/12_dashboard_progress.html

4. Para atualizar o dashboard quando concluir novos itens:
   - Abra data/ccnp_progress.json
   - Incremente o campo 'concluidos' do tópico correspondente
   - Atualize 'ultima_atualizacao' para a data atual
   - Execute o script novamente
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ os.path.abspath() para caminhos absolutos portáveis (Windows/Linux/Mac)
✅ Grade 2x3 com tipos mistos (bar, pie, table) via specs em make_subplots
✅ Barras empilhadas com barmode='stack' e três traces sobrepostos
✅ Donut chart com hole=0.45 no go.Pie
✅ Colorscale numérica em barras: cor proporcional ao valor
✅ Cores condicionais com list comprehension + operador ternário
✅ Zebra striping em tabelas com fill_color e lista multiplicada
✅ Cards de métricas com add_annotation e coordenadas 'paper'
✅ Tema escuro com paper_bgcolor, plot_bgcolor e font global
✅ Loop sobre lista de tuplas para annotations sem repetição de código
✅ f-strings com dados do JSON diretamente no título do dashboard

DIFERENÇA ENTRE SCRIPT 11 E SCRIPT 12:

  Script 11 (v1 — escopo fechado):
  → Usa total e concluidos → mostra X/Y e percentual
  → Ideal quando se sabe antecipadamente quantos itens serão criados
  → Ex: projeto com backlog definido, curso com ementa fixa

  Script 12 (v2 — construção contínua):
  → Usa apenas concluidos como valor absoluto → mede acumulação
  → Ideal para repositórios que crescem sem previsão de total
  → Ex: repositório de estudos, projetos pessoais em evolução

POR QUE SCRIPT AUTOSSUFICIENTE (SEM HELPER):
  Python instalado via Microsoft Store tem sandboxing que impede
  sys.path.insert de funcionar para importar módulos locais.
  A solução é embutir todas as funções no próprio script.
  Vantagem extra: funciona em qualquer ambiente sem configuração.

VARIAÇÕES POSSÍVEIS:
  - Adicionar linha de tendência no comparativo (requer numpy)
  - Exportar tabela como CSV: pandas.DataFrame(metricas).to_csv()
  - Adicionar snapshot de data para histórico de evolução
  - Mudar barmode para 'group' para ver barras lado a lado
"""