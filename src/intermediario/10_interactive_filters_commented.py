#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico Interativo - Filtros Linkados de Latência e Performance (VERSÃO DIDÁTICA)

Visualiza latência vs perda de pacotes com controles interativos:
dropdown (região), botões de toggle (tipo de link) e range slider (latência).
Dois subplots linkados: scatter e box plot de distribuição.
Esta versão contém comentários linha a linha para aprendizado.

Autor: Alexandre Lavorenti Cancilieri
Data: 2026-02-22
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import plotly.graph_objects as go             # Módulo com todos os tipos de trace:
                                              # go.Scatter, go.Box, go.Bar, etc.
from plotly.subplots import make_subplots     # Função para criar grade de subgráficos
import random                                 # Módulo para geração de números aleatórios

# POR QUE PLOTLY PURO (SEM DASH)?
# Todo o HTML gerado é estático — funciona sem servidor Python rodando.
# A interatividade é embutida no HTML via JavaScript interno do Plotly.
# Isso permite hospedar no GitHub Pages, enviar por e-mail, etc.
# Dash seria necessário apenas para callbacks em tempo real com dados externos.

# ============================================================================
# CONFIGURAÇÃO DE REPRODUTIBILIDADE
# ============================================================================

random.seed(42)   # Garante que random.choice/uniform gerem os mesmos valores
                  # em toda execução. Mudar o número gera um novo cenário.

# ============================================================================
# DEFINIR TIPOS DE LINK
# ============================================================================

tipos_link = ['Fibra', 'Wireless', 'MPLS', 'Internet']   # Lista com os 4 tipos de circuito
                                                          # usados na infraestrutura simulada

# ============================================================================
# DEFINIR PALETA DE CORES
# ============================================================================

cores_tipos = {                    # Dicionário: tipo de link → cor hexadecimal
    'Fibra':    '#00CC96',         # Verde-água: melhor performance, mais confiável
    'Wireless': '#FFA15A',         # Laranja: variável, suscetível a interferência
    'MPLS':     '#636EFA',         # Azul: corporativo, SLA dedicado
    'Internet': '#EF553B'          # Vermelho: menos confiável, maior variação
}

# ============================================================================
# DEFINIR REGIÕES DO BRASIL
# ============================================================================

regioes = ['Sudeste', 'Sul', 'Nordeste', 'Centro-Oeste', 'Norte']   # 5 regiões que serão
                                                                      # usadas no dropdown

# ============================================================================
# GERAR 100 LINKS COM CARACTERÍSTICAS REALISTAS POR TIPO
# ============================================================================

links = []                         # Lista vazia que receberá os 100 dicionários de links

for i in range(100):               # Laço que executa 100 vezes (i vai de 0 a 99)

    tipo   = random.choice(tipos_link)   # Escolhe um tipo de link aleatoriamente da lista
    regiao = random.choice(regioes)      # Escolhe uma região aleatoriamente da lista

    if tipo == 'Fibra':                        # Bloco para links de fibra óptica
        latencia  = random.uniform(5, 30)      # Latência entre 5ms e 30ms (mais baixa)
        perda     = random.uniform(0, 1)       # Perda de pacotes entre 0% e 1% (mínima)
        bandwidth = random.uniform(500, 1000)  # Capacidade entre 500 Mbps e 1 Gbps

    elif tipo == 'Wireless':                   # Bloco para links sem fio
        latencia  = random.uniform(15, 80)     # Latência entre 15ms e 80ms (variável)
        perda     = random.uniform(0.5, 5)     # Perda entre 0.5% e 5% (interferências)
        bandwidth = random.uniform(50, 300)    # Capacidade entre 50 e 300 Mbps

    elif tipo == 'MPLS':                       # Bloco para circuitos MPLS dedicados
        latencia  = random.uniform(10, 50)     # Latência entre 10ms e 50ms (controlada por SLA)
        perda     = random.uniform(0, 2)       # Perda entre 0% e 2% (rede privada)
        bandwidth = random.uniform(200, 600)   # Capacidade entre 200 e 600 Mbps

    else:                                      # Bloco para links de Internet pública
        latencia  = random.uniform(30, 150)    # Latência entre 30ms e 150ms (alta variação)
        perda     = random.uniform(1, 8)       # Perda entre 1% e 8% (descarte em congestionamento)
        bandwidth = random.uniform(10, 100)    # Capacidade entre 10 e 100 Mbps (menor)

    links.append({                             # Adiciona dicionário com dados do link à lista
        'id':        f'LINK-{i+1:03d}',        # ID único formatado: LINK-001, LINK-002, ...
                                               # f-string: {i+1:03d} = número com 3 dígitos e zeros à esquerda
        'tipo':      tipo,                     # Tipo do link: 'Fibra', 'Wireless', etc.
        'regiao':    regiao,                   # Região do Brasil onde o link está localizado
        'latencia':  round(latencia, 2),       # Latência em ms, arredondada para 2 casas decimais
        'perda':     round(perda, 2),          # Perda de pacotes em %, arredondada para 2 casas
        'bandwidth': round(bandwidth, 1)       # Capacidade em Mbps, arredondada para 1 casa decimal
    })

# Resultado: lista 'links' com 100 dicionários, cada um representando um circuito de rede

# ============================================================================
# CRIAR FIGURA COM DOIS SUBPLOTS LINKADOS
# ============================================================================

fig = make_subplots(               # Cria figura com grade de subgráficos
    rows=1, cols=2,                # Grade de 1 linha × 2 colunas = 2 subplots lado a lado

    subplot_titles=(               # Tupla com o título de cada subplot (ordem: esq → dir)
        '🔵 Latência vs Perda de Pacotes',          # Título do subplot [row=1, col=1]
        '📊 Distribuição de Latência por Tipo'       # Título do subplot [row=1, col=2]
    ),

    column_widths=[0.6, 0.4],      # Scatter ocupa 60% da largura, box plot 40%
    horizontal_spacing=0.12        # 12% de espaço horizontal entre os dois subplots
)

# ============================================================================
# SUBPLOT 1 (row=1, col=1): SCATTER - LATÊNCIA vs PERDA DE PACOTES
# ============================================================================

for tipo in tipos_link:            # Itera sobre os 4 tipos de link
                                   # Cria um trace separado por tipo para ter legenda individual

    dados_tipo = [l for l in links if l['tipo'] == tipo]   # Filtra apenas os links deste tipo
                                                            # List comprehension com condição

    fig.add_trace(                 # Adiciona um trace (série de dados) à figura
        go.Scatter(                # Tipo scatter: gráfico de dispersão (pontos)

            x=[l['latencia'] for l in dados_tipo],   # Eixo X: latência em ms de cada link
            y=[l['perda']    for l in dados_tipo],   # Eixo Y: perda de pacotes em %

            mode='markers',        # Exibir apenas pontos (sem linhas conectando)

            name=tipo,             # Nome que aparece na legenda para este trace

            legendgroup=tipo,      # Agrupa este trace com o box plot do mesmo tipo
                                   # Clicar no item da legenda oculta AMBOS (scatter + box)

            marker=dict(           # Dicionário com configurações visuais dos marcadores
                size=[max(8, l['bandwidth'] / 40) for l in dados_tipo],
                                   # Tamanho proporcional ao bandwidth do link
                                   # bandwidth / 40 → 1Gbps vira 25px, 100Mbps vira 2.5px
                                   # max(8, ...) → tamanho mínimo de 8px para visibilidade
                color=cores_tipos[tipo],    # Cor do tipo (do dicionário cores_tipos)
                opacity=0.75,              # 75% opaco: permite ver pontos sobrepostos
                line=dict(                 # Borda de cada ponto
                    width=1,              # Espessura da borda: 1px
                    color='white'         # Borda branca: destaca os pontos no fundo cinza
                )
            ),

            text=[                 # Lista de strings para o tooltip de cada ponto
                f"ID: {l['id']}<br>Região: {l['regiao']}<br>Bandwidth: {l['bandwidth']} Mbps"
                for l in dados_tipo          # <br> = quebra de linha no HTML do tooltip
            ],

            hovertemplate=(        # Template do tooltip ao passar o mouse sobre o ponto
                '<b>%{text}</b><br>'          # %{text} = valor do campo 'text' acima (em negrito)
                'Latência: %{x} ms<br>'       # %{x} = valor do eixo X (latência)
                'Perda: %{y}%<br>'            # %{y} = valor do eixo Y (perda)
                '<extra>' + tipo + '</extra>' # <extra> = caixinha colorida lateral do tooltip
            )
        ),
        row=1, col=1               # Posicionar este trace no subplot da esquerda [1,1]
    )

# ---- Zona de performance ótima ----

fig.add_shape(                     # Adiciona uma forma geométrica ao gráfico
    type='rect',                   # Tipo retângulo
    x0=0,  y0=0,                   # Canto inferior esquerdo: (0ms, 0% perda)
    x1=50, y1=2,                   # Canto superior direito: (50ms, 2% perda)
                                   # Define a "zona ótima": latência < 50ms E perda < 2%
    fillcolor='rgba(0, 204, 150, 0.08)',        # Verde muito transparente (8% opacidade)
    line=dict(                                  # Borda do retângulo
        color='rgba(0, 204, 150, 0.5)',         # Verde semi-transparente
        dash='dot'                              # Linha pontilhada
    ),
    row=1, col=1                   # Aplicar no subplot [1,1]
)

fig.add_annotation(                # Adiciona texto flutuante ao gráfico
    x=25, y=1,                     # Posição: centro da zona ótima (25ms, 1%)
    text='✅ Zona Ótima',           # Texto exibido
    showarrow=False,               # Não mostrar seta apontando para o ponto
    font=dict(size=10, color='#00CC96'),   # Fonte pequena na cor verde
    row=1, col=1                   # Aplicar no subplot [1,1]
)

fig.update_xaxes(                  # Configura o eixo X do subplot especificado
    title_text='Latência (ms)',    # Rótulo do eixo X
    range=[0, 160],                # Limites iniciais: 0 a 160ms (maior que o slider padrão)
    row=1, col=1                   # Aplicar somente no subplot [1,1]
)

fig.update_yaxes(                  # Configura o eixo Y do subplot especificado
    title_text='Perda de Pacotes (%)',   # Rótulo do eixo Y
    row=1, col=1                         # Aplicar somente no subplot [1,1]
)

# ============================================================================
# SUBPLOT 2 (row=1, col=2): BOX PLOT - DISTRIBUIÇÃO DE LATÊNCIA
# ============================================================================

# Box plot mostra a distribuição estatística de latência para cada tipo de link:
# mínimo, Q1 (25%), mediana (50%), Q3 (75%), máximo e outliers
# Complementa o scatter: scatter = correlação entre variáveis,
#                         box    = distribuição de uma variável por categoria

for tipo in tipos_link:            # Itera sobre os 4 tipos (mesma ordem do scatter)

    dados_tipo = [l for l in links if l['tipo'] == tipo]   # Filtra links deste tipo

    fig.add_trace(                 # Adiciona trace de box plot
        go.Box(                    # Tipo Box: diagrama de caixa e bigodes

            y=[l['latencia'] for l in dados_tipo],   # Valores da distribuição (eixo Y)
                                                      # Box plot vertical: dados no eixo Y

            name=tipo,             # Nome na legenda (mesmo que o scatter correspondente)

            legendgroup=tipo,      # MESMO legendgroup do scatter do mesmo tipo
                                   # Garante que clique na legenda oculte ambos

            showlegend=False,      # NÃO exibir item de legenda separado para o box
                                   # Evita duplicar: o scatter já aparece na legenda

            marker_color=cores_tipos[tipo],   # Cor da caixa e bigodes (mesmo do scatter)

            boxmean='sd',          # Exibir média (linha tracejada) e desvio padrão
                                   # 'sd' = standard deviation
                                   # True = apenas média, False = nenhum dos dois

            hovertemplate=(        # Template do tooltip do box plot
                '<b>' + tipo + '</b><br>'             # Nome do tipo em negrito
                'Mediana: %{median} ms<br>'           # %{median} = mediana calculada
                'Q1: %{q1} ms | Q3: %{q3} ms<br>'    # %{q1} e %{q3} = quartis 25% e 75%
                '<extra></extra>'                     # <extra> vazio = remove caixinha lateral
            )
        ),
        row=1, col=2               # Posicionar no subplot da direita [1,2]
    )

fig.update_yaxes(                  # Configura eixo Y do subplot [1,2]
    title_text='Latência (ms)',    # Rótulo do eixo Y do box plot
    row=1, col=2                   # Aplicar somente no subplot [1,2]
)

# ============================================================================
# CONSTRUIR BOTÕES DO DROPDOWN - FILTRO POR REGIÃO
# ============================================================================

# O dropdown usa method='restyle' para substituir os dados x/y dos traces.
# 'restyle' não recria os traces — apenas atualiza os valores de propriedades.
# Isso é mais eficiente que recriar a figura inteira a cada clique.
#
# ESTRUTURA DOS TRACES NA FIGURA (ordem de inserção com add_trace):
# Índice 0: Scatter Fibra      → subplot [1,1]
# Índice 1: Scatter Wireless   → subplot [1,1]
# Índice 2: Scatter MPLS       → subplot [1,1]
# Índice 3: Scatter Internet   → subplot [1,1]
# Índice 4: Box Fibra          → subplot [1,2]
# Índice 5: Box Wireless       → subplot [1,2]
# Índice 6: Box MPLS           → subplot [1,2]
# Índice 7: Box Internet       → subplot [1,2]

botoes_regiao = []                 # Lista que armazenará todos os botões do dropdown

opcoes_regiao = ['Todas as Regiões'] + regioes   # Concatena: primeira opção = sem filtro
                                                  # Resultado: ['Todas as Regiões', 'Sudeste', ...]

for opcao in opcoes_regiao:        # Cria um botão para cada opção (6 botões no total)

    novos_x_scatter    = []        # Novas coordenadas X para os 4 traces scatter
    novos_y_scatter    = []        # Novas coordenadas Y para os 4 traces scatter
    novos_text_scatter = []        # Novo texto do tooltip para os 4 traces scatter
    novos_size_scatter = []        # Novo tamanho dos pontos para os 4 traces scatter
    novos_y_box        = []        # Novos valores Y para os 4 traces box

    for tipo in tipos_link:        # Para cada tipo, filtra os dados da região selecionada

        if opcao == 'Todas as Regiões':                          # Sem filtro de região
            filtrado = [l for l in links if l['tipo'] == tipo]
        else:                                                    # Com filtro de região
            filtrado = [l for l in links if l['tipo'] == tipo and l['regiao'] == opcao]

        novos_x_scatter.append([l['latencia'] for l in filtrado])   # Latências filtradas

        novos_y_scatter.append([l['perda'] for l in filtrado])      # Perdas filtradas

        novos_text_scatter.append([              # Textos do tooltip filtrados
            f"ID: {l['id']}<br>Região: {l['regiao']}<br>Bandwidth: {l['bandwidth']} Mbps"
            for l in filtrado
        ])

        novos_size_scatter.append(               # Tamanhos dos pontos filtrados
            [max(8, l['bandwidth'] / 40) for l in filtrado]
        )

        novos_y_box.append(                      # Latências para o box plot filtrado
            [l['latencia'] for l in filtrado]
        )

    # Após o loop interno: cada lista tem 4 elementos (um por tipo de link)

    botoes_regiao.append(dict(             # Adiciona botão à lista do dropdown
        label=opcao,                       # Texto exibido no dropdown para esta opção
        method='restyle',                  # Método: atualiza propriedades dos traces
                                           # (não recria a figura, apenas troca os dados)

        # DOIS PARES [dados, índices]: garante que scatter e box recebam
        # apenas os seus próprios dados, sem interferência entre os grupos.
        # Se misturássemos tudo em um único dict, o Plotly aplica na ordem
        # dos traces e listas de tamanhos diferentes causam sobreposição errada.

        args=[                             # args[0]: atualiza os 4 traces scatter
            {
                'x':           novos_x_scatter,      # Coordenadas X filtradas (latência)
                'y':           novos_y_scatter,      # Coordenadas Y filtradas (perda)
                'text':        novos_text_scatter,   # Tooltips filtrados
                'marker.size': novos_size_scatter,   # Tamanhos dos pontos filtrados
            },
            [0, 1, 2, 3]   # Índices dos traces scatter (Fibra, Wireless, MPLS, Internet)
        ],

        args2=[                            # args2: atualiza os 4 traces box
            {'y': novos_y_box},            # Valores Y do box plot filtrados (latência)
            [4, 5, 6, 7]   # Índices dos traces box (Fibra, Wireless, MPLS, Internet)
        ]
    ))

# ============================================================================
# CONSTRUIR BOTÕES DE TOGGLE - FILTRO POR TIPO DE LINK
# ============================================================================

# Os botões de toggle usam method='update' para controlar a visibilidade dos traces.
# 'update' pode alterar dados E layout ao mesmo tempo.
# Aqui usamos apenas para a propriedade 'visible' de cada trace.

n = len(tipos_link)    # n = 4 (número de tipos de link)
                       # Total de traces = n * 2 = 8 (4 scatter + 4 box)

botoes_tipo = [dict(             # Primeiro botão: mostrar todos os tipos
    label='Todos',               # Texto exibido no botão
    method='update',             # Método: pode alterar dados e layout simultaneamente
    args=[{'visible': [True] * (n * 2)}]   # Torna todos os 8 traces visíveis
                                            # [True] * 8 = [True, True, ..., True]
)]

for i, tipo in enumerate(tipos_link):    # enumerate(): retorna (índice, valor)
                                          # i=0:Fibra, i=1:Wireless, i=2:MPLS, i=3:Internet

    vis = [False] * (n * 2)    # Começa com todos os 8 traces ocultos

    vis[i]     = True           # Ativa o scatter do tipo i (índices 0, 1, 2, 3)
    vis[i + n] = True           # Ativa o box do tipo i (índices 4, 5, 6, 7)
                                # Exemplo: i=1 (Wireless) → vis[1]=True e vis[5]=True

    botoes_tipo.append(dict(    # Adiciona botão de toggle para este tipo
        label=tipo,             # Texto do botão: 'Fibra', 'Wireless', etc.
        method='update',        # Método update para controlar visibilidade
        args=[{'visible': vis}] # Lista de 8 booleans: True apenas para os traces deste tipo
    ))

# ============================================================================
# CONSTRUIR STEPS DO RANGE SLIDER - FAIXA DE LATÊNCIA
# ============================================================================

# O slider usa method='relayout' para alterar propriedades do layout.
# 'xaxis.range' define os limites mínimo e máximo visíveis do eixo X do scatter.
# Apenas o scatter é afetado (o box plot usa eixo Y para os dados).

faixas_latencia = [                    # Lista de tuplas: (rótulo, [mínimo, máximo])
    ('0–50 ms',   [0,   50]),          # Apenas links de baixa latência (tipicamente Fibra)
    ('0–80 ms',   [0,   80]),          # Fibra + MPLS + parte do Wireless
    ('0–150 ms',  [0,  150]),          # Visão completa (padrão — active=2)
    ('50–150 ms', [50, 150]),          # Foco nos links com latência alta (Internet/Wireless)
]

steps_slider = []                      # Lista que armazenará os steps do slider

for label, rng in faixas_latencia:     # Desempacota cada tupla: label=rótulo, rng=[min, max]

    steps_slider.append(dict(          # Adiciona step à lista
        label=label,                   # Texto exibido abaixo do marcador no slider
        method='relayout',             # Método: altera propriedades do layout (não dos dados)
        args=[{'xaxis.range': rng}]    # Altera o range do eixo X do primeiro subplot
                                       # 'xaxis' = eixo X do subplot [1,1]
                                       # 'xaxis2' seria o eixo X do subplot [1,2]
    ))

# ============================================================================
# LAYOUT GLOBAL DO DASHBOARD
# ============================================================================

fig.update_layout(                     # Aplica configurações globais a toda a figura

    title=dict(                        # Configuração do título principal
        text=(
            '🔍 Análise Interativa de Performance de Links<br>'
            '<sub>Use os controles abaixo para filtrar por região, tipo e faixa de latência</sub>'
                                       # <sub>...</sub> = subtítulo em fonte menor
        ),
        x=0.5,                         # Posição horizontal: 0.5 = centro da figura
        xanchor='center',              # Âncora do título no ponto x=0.5
        font=dict(size=20)             # Tamanho da fonte do título principal
    ),

    height=650,                        # Altura total da figura em pixels

    plot_bgcolor='#F8F9FA',            # Cor de fundo da área dos gráficos (cinza muito claro)
    paper_bgcolor='white',             # Cor de fundo de toda a figura (fora dos subplots)

    font=dict(family='Arial', size=12),   # Fonte padrão aplicada a todos os textos

    legend=dict(                       # Configuração da legenda global (compartilhada)
        title=dict(text='Tipo de Link'),   # Título da caixa de legenda
        orientation='h',               # Horizontal: itens lado a lado
        yanchor='bottom',              # Âncora vertical: base da legenda
        y=1.10,                        # Posição Y: 10% acima do topo da área de plotagem
        xanchor='center',              # Âncora horizontal: centro
        x=0.5                          # Posição X: centro da figura
    ),

    hovermode='closest',               # Tooltip aparece para o ponto mais próximo do cursor

    margin=dict(t=180, b=120),         # Margens extras:
                                       # t=180px: espaço no topo para legenda + controles
                                       # b=120px: espaço na base para o slider

    # ========================================================================
    # UPDATEMENUS: lista de menus interativos (dropdown ou botões)
    # Cada elemento da lista é um menu independente posicionado na figura
    # ========================================================================

    updatemenus=[

        # --- Menu 1: Dropdown - Filtro por Região ---
        dict(
            buttons=botoes_regiao,     # Lista de 6 botões construída acima
            direction='down',          # Tipo dropdown: abre lista para baixo ao clicar
            showactive=True,           # Destaca visualmente a opção atualmente selecionada
            x=0.00,                    # Posição X: 0 = canto esquerdo da figura
            xanchor='left',            # Âncora no lado esquerdo do menu
            y=1.30,                    # Posição Y: 30% acima do topo da área de plotagem
            yanchor='top',             # Âncora no topo do menu
            bgcolor='white',           # Fundo branco para o dropdown
            bordercolor='#aaaaaa',     # Borda cinza clara
            font=dict(size=12)         # Tamanho da fonte das opções
        ),

        # --- Menu 2: Botões Toggle - Filtro por Tipo de Link ---
        dict(
            buttons=botoes_tipo,       # Lista de 5 botões construída acima
            type='buttons',            # Renderiza como botões separados (não dropdown)
            direction='right',         # Botões dispostos da esquerda para a direita
            showactive=True,           # Destaca o botão atualmente ativo
            x=0.50,                    # Posição X: centro da figura
            xanchor='center',          # Âncora no centro do grupo de botões
            y=1.30,                    # Mesma altura vertical do dropdown
            yanchor='top',             # Âncora no topo
            bgcolor='#F0F0F0',         # Fundo cinza claro para os botões
            bordercolor='#aaaaaa',     # Borda cinza clara
            font=dict(size=11)         # Fonte ligeiramente menor que o dropdown
        ),
    ],

    # ========================================================================
    # SLIDERS: lista de controles deslizantes
    # Cada elemento da lista é um slider independente posicionado na figura
    # ========================================================================

    sliders=[dict(                     # Lista com 1 slider

        steps=steps_slider,            # Lista de 4 steps construída acima

        active=2,                      # Índice do step ativo ao carregar a página
                                       # active=2 → '0–150 ms' (terceiro step, índice 2)

        currentvalue=dict(             # Configuração do texto que mostra o valor atual
            prefix='Faixa de Latência: ',   # Prefixo exibido antes do rótulo do step ativo
            font=dict(size=12, color='#333'),   # Fonte e cor do texto de valor atual
            xanchor='center',          # Centralizar o texto acima do slider
            visible=True               # True = exibir o texto do valor atual
        ),

        x=0.00,                        # Posição X: começa no canto esquerdo
        len=0.60,                      # Comprimento do slider: 60% da largura total da figura
        y=-0.18,                       # Posição Y: 18% abaixo da base da área de plotagem

        pad=dict(t=30, b=10),          # Padding interno: 30px acima, 10px abaixo do slider

        bgcolor='#F0F0F0',             # Cor de fundo da trilha do slider
        bordercolor='#aaaaaa',         # Cor da borda do slider
        tickcolor='#888888',           # Cor das marcações dos steps na trilha
        font=dict(size=11)             # Tamanho da fonte dos rótulos dos steps
    )],

    # ========================================================================
    # ANNOTATIONS: textos flutuantes usados como rótulos dos controles
    # xref/yref='paper' = coordenadas relativas à figura (0=esq/baixo, 1=dir/cima)
    # ========================================================================

    annotations=[

        dict(                          # Rótulo identificador do dropdown de região
            text='🌎 Filtrar por Região:',   # Texto do rótulo
            x=0.00,                    # Posição X: alinhado com o dropdown
            y=1.35,                    # Posição Y: acima do dropdown (y=1.30)
            xref='paper',              # Coordenada X relativa ao paper (0 a 1)
            yref='paper',              # Coordenada Y relativa ao paper (0 a 1)
            showarrow=False,           # Sem seta — apenas texto flutuante
            font=dict(size=11, color='#444')   # Fonte cinza escuro
        ),

        dict(                          # Rótulo identificador dos botões de tipo
            text='🔗 Filtrar por Tipo:',      # Texto do rótulo
            x=0.38,                    # Posição X: à esquerda do centro (onde começam os botões)
            y=1.35,                    # Mesma altura do rótulo de região
            xref='paper',              # Coordenada relativa ao paper
            yref='paper',              # Coordenada relativa ao paper
            showarrow=False,           # Sem seta
            font=dict(size=11, color='#444')   # Mesma fonte do rótulo anterior
        ),
    ]
)

# ============================================================================
# EXPORTAR PARA HTML
# ============================================================================

fig.write_html('../../docs/10_interactive_filters.html')   # Salva a figura como HTML interativo
                                                            # O arquivo contém todo o JavaScript
                                                            # do Plotly embutido (standalone)
                                                            # Funciona sem servidor Python

print("✅ Gráfico salvo em: docs/10_interactive_filters.html")   # Confirmação no terminal

# ============================================================================
# EXIBIR ESTATÍSTICAS NO TERMINAL
# ============================================================================

print(f"\n📊 Resumo:")
print(f"  🔗 Total de links simulados : {len(links)}")              # Quantidade total gerada
print(f"  📡 Tipos de link            : {', '.join(tipos_link)}")   # Lista os 4 tipos
print(f"  🌎 Regiões                  : {', '.join(regioes)}")      # Lista as 5 regiões
print(f"  🎛️  Controles               : Dropdown (região) | Toggle (tipo) | Slider (latência)")

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Certifique-se de ter Plotly instalado:
   pip install plotly

2. Execute o script:
   python src/intermediario/10_interactive_filters_commented.py

3. Abra o arquivo gerado:
   docs/10_interactive_filters.html no navegador

4. Interaja com os controles:
   - Dropdown "Filtrar por Região" → filtra os dados em AMBOS os subplots
   - Botões "Filtrar por Tipo"     → mostra/oculta séries por tipo de link
   - Slider inferior               → ajusta a faixa de latência visível no scatter
   - Legenda (clique)              → mostra/oculta scatter + box do mesmo tipo
   - Zoom nativo do Plotly         → arraste para ampliar uma área específica
   - Double click                  → restaura o zoom original

5. Experimente modificar:
   - Aumente para 200 links (range(200)) para mais dados
   - Adicione nova região à lista 'regioes' e re-execute
   - Crie novo step no slider (ex: '0–30 ms' para visualizar apenas Fibra)
   - Mude o tamanho dos pontos para ser proporcional à latência ao invés de bandwidth
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ Criar subplots com tipos diferentes (Scatter + Box) lado a lado
✅ Usar legendgroup para vincular traces na legenda (clique oculta ambos)
✅ Implementar dropdown com method='restyle' (substitui dados dos traces)
✅ Implementar botões toggle com method='update' (controla visibilidade)
✅ Implementar slider com method='relayout' (altera range do eixo X)
✅ Adicionar shapes (retângulo de fundo) e annotations a subplots específicos
✅ Usar margin para reservar espaço para controles externos à área de plotagem
✅ Dimensionar pontos do scatter proporcionalmente a uma terceira variável (bandwidth)
✅ Usar boxmean='sd' para exibir média e desvio padrão no box plot

OS TRÊS MÉTODOS DE INTERATIVIDADE NO PLOTLY PURO:

┌─────────────┬──────────────────────────────────────┬──────────────────────┐
│ Método      │ O que altera                         │ Uso neste script     │
├─────────────┼──────────────────────────────────────┼──────────────────────┤
│ restyle     │ Dados dos traces (x, y, text, size)  │ Dropdown de região   │
│ relayout    │ Layout (eixos, títulos, ranges)       │ Slider de latência   │
│ update      │ Dados + layout simultaneamente        │ Toggle de tipo       │
└─────────────┴──────────────────────────────────────┴──────────────────────┘

ÍNDICES DOS TRACES (essencial para restyle e update):
- Os traces são indexados na ORDEM EM QUE FORAM ADICIONADOS com add_trace()
- Neste script: índices 0-3 = scatter (4 tipos), índices 4-7 = box (4 tipos)
- Sempre documente a ordem dos traces para não errar ao construir args[]

TIPOS DE CONTROLE EM UPDATEMENUS:
- direction='down' + sem 'type'       → Dropdown (lista vertical)
- type='buttons' + direction='right'  → Botões horizontais lado a lado

DIFERENÇA ENTRE PLOTLY PURO E DASH:
- Plotly puro : HTML estático, sem servidor, interatividade pré-calculada
  → Ideal para: GitHub Pages, e-mail, relatórios offline, portfólio
- Dash        : aplicação web com servidor Python, callbacks em tempo real
  → Ideal para: dashboards corporativos, dados ao vivo, filtros complexos

APLICAÇÕES EM REDES (CCNP ENCORE):
- Análise de SLA por tipo de circuito (MPLS vs Internet vs Fibra)
- Comparação de performance por região geográfica
- Troubleshooting de latência: identificar outliers por tipo de link
- Relatório de QoS: correlação entre largura de banda e qualidade do link
- Dashboard de NOC: filtrar alarmes por localidade e tipo de circuito
"""

# ============================================================================
# VARIAÇÕES POSSÍVEIS
# ============================================================================
"""
ADICIONAR BOTÃO "RESETAR ZOOM":
dict(
    label='↺ Reset',
    method='relayout',
    args=[{'xaxis.range': [0, 160], 'yaxis.range': [0, 10]}]
)

COLORIR PONTOS DINAMICAMENTE POR REGIÃO (ao invés de tipo):
marker=dict(
    color=[cores_regioes[l['regiao']] for l in dados_tipo],
    colorscale='Viridis',
    showscale=True
)

ADICIONAR LINHA DE TENDÊNCIA (TRENDLINE) AO SCATTER:
import numpy as np
z = np.polyfit(x_vals, y_vals, 1)         # Regressão linear de grau 1
p = np.poly1d(z)                           # Polinômio resultante
x_line = [min(x_vals), max(x_vals)]
y_line = [p(x) for x in x_line]
fig.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines', name='Tendência'))

EXPORTAR COMO IMAGEM ESTÁTICA:
fig.write_image('docs/10_interactive_filters.png')   # Requer: pip install kaleido
"""