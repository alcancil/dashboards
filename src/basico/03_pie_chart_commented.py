#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico de Pizza - Distribuição de Labs por Categoria (VERSÃO DIDÁTICA)

Visualiza a proporção de labs em diferentes categorias de conteúdo.
Esta versão contém comentários linha a linha para aprendizado.

Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-12
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import plotly.graph_objects as go  # Biblioteca para gráficos interativos

# ============================================================================
# DADOS DO GRÁFICO
# ============================================================================

# Lista com nomes das categorias de labs
# Agrupa labs por tema/assunto principal
categorias = [
    'QoS',                  # Quality of Service - maior grupo
    'VRF-Lite',             # Virtual Routing and Forwarding
    'Python/Automação',     # Scripts de automação
    'Multicast',            # Multicast routing
    'Virtualização',        # VMs, Hypervisors, etc
    'Outros'                # Diversos tópicos menores
]

# Quantidade de labs em cada categoria
# Esses valores determinam o tamanho de cada fatia
quantidade = [24, 4, 21, 4, 18, 8]

# Total: 79 labs
# Plotly calcula automaticamente os percentuais

# ============================================================================
# PALETA DE CORES
# ============================================================================

# Cores específicas para cada categoria
# Mesma paleta dos gráficos anteriores (consistência visual)
cores = [
    '#667eea',  # QoS - Roxo/Azul
    '#764ba2',  # VRF-Lite - Roxo escuro
    '#f093fb',  # Python/Automação - Rosa claro
    '#4facfe',  # Multicast - Azul claro
    '#43e97b',  # Virtualização - Verde
    '#fa709a'   # Outros - Rosa
]

# ============================================================================
# CRIAR FIGURA (GRÁFICO)
# ============================================================================

# Figure() cria um objeto de gráfico vazio
fig = go.Figure()

# ============================================================================
# ADICIONAR PIZZA NO GRÁFICO
# ============================================================================

# add_trace() adiciona um elemento visual ao gráfico
# Pie() cria gráfico de pizza/donut
fig.add_trace(go.Pie(
    labels=categorias,                   # Nomes das fatias
    values=quantidade,                   # Valores (tamanho das fatias)
    marker=dict(
        colors=cores,                    # Lista de cores (uma para cada fatia)
        line=dict(
            color='white',               # Cor da borda entre fatias
            width=2                      # Espessura da borda em pixels
        )
    ),
    hole=0.4,                            # Tamanho do buraco central
                                         # 0 = pizza cheia
                                         # 0.4 = donut (40% de buraco)
                                         # 0.7 = anel fino
    textposition='auto',                 # Posição automática do texto
                                         # Plotly escolhe melhor posição
    textinfo='label+percent',            # O que mostrar em cada fatia
                                         # 'label' = nome da categoria
                                         # 'percent' = percentual
                                         # 'value' = número absoluto
                                         # Pode combinar: 'label+percent+value'
    hovertemplate=(                      # Template customizado do tooltip
        '<b>%{label}</b><br>' +          # Nome da categoria em negrito
        'Labs: %{value}<br>' +           # Quantidade absoluta
        'Percentual: %{percent}<br>' +   # Percentual calculado
        '<extra></extra>'                # Remove trace name
    )
))

# ============================================================================
# CONFIGURAR APARÊNCIA DO GRÁFICO
# ============================================================================

# update_layout() personaliza títulos, legenda, tamanho, etc
fig.update_layout(
    title='Distribuição de Labs por Categoria',  # Título principal
    template='plotly_white',                      # Tema visual (fundo branco)
    height=500,                                   # Altura do gráfico em pixels
    showlegend=True,                              # Mostrar legenda (importante!)
    legend=dict(
        orientation="v",         # Orientação vertical (v) ou horizontal (h)
        yanchor="middle",        # Âncora vertical (middle = centro)
        y=0.5,                   # Posição Y (0.5 = meio da página)
        xanchor="left",          # Âncora horizontal (left = esquerda)
        x=1.05                   # Posição X (1.05 = um pouco à direita do gráfico)
    )
)

# ============================================================================
# ADICIONAR ANOTAÇÃO NO CENTRO (DONUT)
# ============================================================================

# add_annotation() adiciona texto em qualquer posição do gráfico
# Útil para mostrar total no centro do donut
fig.add_annotation(
    text=f'<b>{sum(quantidade)}</b><br>Labs<br>Total',  # Texto com HTML
                                                         # sum() calcula total
                                                         # <b> = negrito
                                                         # <br> = quebra de linha
    x=0.5,                                  # Posição X (0.5 = centro horizontal)
    y=0.5,                                  # Posição Y (0.5 = centro vertical)
    font=dict(
        size=20,                            # Tamanho da fonte
        color='#667eea'                     # Cor do texto (mesma do tema)
    ),
    showarrow=False                         # Não mostrar seta apontando
)

# ============================================================================
# EXPORTAR PARA HTML
# ============================================================================

# write_html() salva o gráfico como página web interativa
fig.write_html('../../docs/03_pie_chart.html')

# Mensagem de confirmação no terminal
print("✅ Gráfico salvo em: docs/03_pie_chart.html")

# Calcular e mostrar estatísticas
total = sum(quantidade)
maior_categoria = categorias[quantidade.index(max(quantidade))]
print(f"📊 Total de labs: {total}")
print(f"🏆 Maior categoria: {maior_categoria} ({max(quantidade)} labs)")

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Certifique-se de ter Plotly instalado:
   pip install plotly

2. Execute o script:
   python src/basico/03_pie_chart_commented.py

3. Abra o arquivo gerado:
   docs/03_pie_chart.html no navegador

4. Experimente modificar:
   - Mude 'hole' para 0 (pizza cheia) ou 0.7 (anel fino)
   - Troque 'textinfo' para 'label+value' (mostrar números)
   - Remova 'showlegend=True' para esconder legenda
   - Mude posição da legenda (x=0.1, y=1.1 para topo)
   - Adicione 'pull=[0.1, 0, 0, 0, 0, 0]' no go.Pie() para destacar primeira fatia
   
5. Execute novamente para ver as mudanças!
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ Criar gráfico de pizza com go.Pie()
✅ Transformar pizza em donut (hole parameter)
✅ Plotly calcula percentuais automaticamente
✅ Customizar texto exibido (textinfo)
✅ Posicionar legenda de forma customizada
✅ Adicionar anotações em posições específicas
✅ Usar HTML em textos (negrito, quebras de linha)
✅ Calcular estatísticas dos dados (sum, max, index)

DIFERENÇAS DOS GRÁFICOS ANTERIORES:
- Linha: go.Scatter() - mostra tendência temporal
- Barras: go.Bar() - compara valores absolutos
- Pizza: go.Pie() - mostra proporções/percentuais

QUANDO USAR PIZZA:
✅ Mostrar partes de um todo (100%)
✅ Comparar proporções (qual % cada categoria representa)
✅ Até 6-7 categorias (mais que isso fica confuso)

QUANDO NÃO USAR PIZZA:
❌ Comparar valores que não somam 100%
❌ Muitas categorias (>8)
❌ Valores muito próximos (difícil ver diferença)
❌ Mudanças ao longo do tempo (use linha)
"""

# ============================================================================
# VARIAÇÕES POSSÍVEIS
# ============================================================================
"""
PIZZA CHEIA (SEM BURACO):
fig.add_trace(go.Pie(
    labels=categorias,
    values=quantidade,
    hole=0  # Sem buraco = pizza completa
))

DESTACAR UMA FATIA (PULL):
fig.add_trace(go.Pie(
    labels=categorias,
    values=quantidade,
    pull=[0.1, 0, 0, 0, 0, 0]  # Primeira fatia puxada para fora
))

MOSTRAR APENAS PERCENTUAIS:
textinfo='percent'

MOSTRAR TUDO:
textinfo='label+percent+value'

LEGENDA NO TOPO:
legend=dict(orientation="h", x=0.5, y=1.1)

ROTACIONAR PIZZA:
rotation=90  # Rotaciona 90 graus
"""