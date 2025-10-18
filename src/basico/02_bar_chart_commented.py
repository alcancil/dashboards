#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico de Barras - Comparação de Labs por Domínio CCNP (VERSÃO DIDÁTICA)

Visualiza quantidade de labs completados em cada domínio do ENCOR 350-401.
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

# Lista com nomes dos 6 domínios do CCNP ENCOR (eixo X)
# Esses são os domínios oficiais da certificação 350-401
dominios = [
    'Architecture',           # Domínio 1 - Arquitetura de redes
    'Virtualization',         # Domínio 2 - Virtualização
    'Infrastructure',         # Domínio 3 - Infraestrutura (maior peso)
    'Network Assurance',      # Domínio 4 - Garantia de rede
    'Security',               # Domínio 5 - Segurança
    'Automation'              # Domínio 6 - Automação e programabilidade
]

# Quantidade de labs completados por domínio (eixo Y)
# Valores reais do meu progresso nos estudos
labs_completos = [24, 18, 6, 0, 0, 21]

# Peso de cada domínio na prova (informação adicional - não usado no gráfico)
# Útil para ver onde focar mais estudos
peso_prova = [30, 10, 30, 10, 20, 15]  # Percentual na prova ENCOR

# ============================================================================
# PALETA DE CORES
# ============================================================================

# Cores específicas para cada domínio (gradiente roxo → rosa)
# Usar cores diferentes facilita identificação visual
cores = [
    '#667eea',  # Architecture - Roxo/Azul
    '#764ba2',  # Virtualization - Roxo escuro
    '#f093fb',  # Infrastructure - Rosa claro
    '#4facfe',  # Network Assurance - Azul claro
    '#43e97b',  # Security - Verde
    '#fa709a'   # Automation - Rosa
]

# ============================================================================
# CRIAR FIGURA (GRÁFICO)
# ============================================================================

# Figure() cria um objeto de gráfico vazio
fig = go.Figure()

# ============================================================================
# ADICIONAR BARRAS NO GRÁFICO
# ============================================================================

# add_trace() adiciona um elemento visual ao gráfico
# Bar() cria barras verticais (para horizontal, use orientation='h')
fig.add_trace(go.Bar(
    x=dominios,                          # Categorias no eixo X (horizontal)
    y=labs_completos,                    # Valores no eixo Y (altura das barras)
    marker=dict(
        color=cores,                     # Lista de cores (uma para cada barra)
        line=dict(
            color='white',               # Cor da borda das barras
            width=2                      # Espessura da borda em pixels
        )
    ),
    text=labs_completos,                 # Mostrar valores no topo das barras
    textposition='outside',              # Posição do texto (fora/acima da barra)
    hovertemplate=(                      # Template customizado do tooltip
        '<b>%{x}</b><br>' +              # %{x} = nome do domínio em negrito
        'Labs: %{y}<br>' +               # %{y} = quantidade de labs
        '<extra></extra>'                # Remove trace name do hover
    )
))

# ============================================================================
# CONFIGURAR APARÊNCIA DO GRÁFICO
# ============================================================================

# update_layout() personaliza títulos, eixos, tamanho, etc
fig.update_layout(
    title='Labs por Domínio CCNP ENCOR',           # Título principal do gráfico
    xaxis_title='Domínio',                         # Título do eixo X
    yaxis_title='Número de Labs',                  # Título do eixo Y
    template='plotly_white',                       # Tema visual (fundo branco)
    height=500,                                    # Altura do gráfico em pixels
    showlegend=False,                              # Não mostrar legenda (não precisa)
    yaxis=dict(
        range=[0, max(labs_completos) + 5]         # Range do eixo Y (0 até max + espaço)
    )
)

# ============================================================================
# EXPORTAR PARA HTML
# ============================================================================

# write_html() salva o gráfico como página web interativa
fig.write_html('../../docs/02_bar_chart.html')

# Mensagem de confirmação no terminal
print("✅ Gráfico salvo em: docs/02_bar_chart.html")

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Certifique-se de ter Plotly instalado:
   pip install plotly

2. Execute o script:
   python src/basico/02_bar_chart_commented.py

3. Abra o arquivo gerado:
   docs/02_bar_chart.html no navegador

4. Experimente modificar:
   - Mude os valores em 'labs_completos' com seus dados reais
   - Troque as cores em 'cores' (use códigos hexadecimais)
   - Mude 'textposition' para 'inside' (texto dentro da barra)
   - Adicione 'orientation="h"' no go.Bar() para barras horizontais
   
5. Execute novamente para ver as mudanças!
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ Criar gráfico de barras com go.Bar()
✅ Usar cores diferentes para cada categoria
✅ Adicionar valores no topo das barras (text/textposition)
✅ Customizar hover tooltip (hovertemplate)
✅ Adicionar bordas nas barras (marker.line)
✅ Controlar range do eixo Y
✅ Remover legenda quando não necessária
✅ Usar listas paralelas (dominios, labs, cores)

DIFERENÇAS DO GRÁFICO DE LINHA:
- Linha usa go.Scatter() → Barras usa go.Bar()
- Linha conecta pontos → Barras compara categorias
- Linha mostra tendência → Barras mostram comparação
"""

# ============================================================================
# VARIAÇÕES POSSÍVEIS
# ============================================================================
"""
BARRAS HORIZONTAIS:
fig.add_trace(go.Bar(
    x=labs_completos,  # Inverte
    y=dominios,        # Inverte
    orientation='h'    # Horizontal
))

BARRAS AGRUPADAS (múltiplas séries):
fig.add_trace(go.Bar(name='Completos', x=dominios, y=labs_completos))
fig.add_trace(go.Bar(name='Planejados', x=dominios, y=[10, 5, 20, 15, 10, 5]))
fig.update_layout(barmode='group')

BARRAS EMPILHADAS:
fig.update_layout(barmode='stack')
"""