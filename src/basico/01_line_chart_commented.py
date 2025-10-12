#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico de Linha - Progresso Semanal de Labs (VERSÃO DIDÁTICA)

Cria visualização do progresso de labs CCNP ao longo das semanas.
Esta versão contém comentários linha a linha para aprendizado.

Autor: Alexandre Cancilieri
Data: 2025-10-11
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import plotly.graph_objects as go  # Biblioteca para gráficos interativos

# ============================================================================
# DADOS DO GRÁFICO
# ============================================================================

# Lista com número das semanas (eixo X)
# Representa as 12 semanas de estudo
semanas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# Lista com total acumulado de labs (eixo Y)
# Cada valor é o total de labs completados até aquela semana
# Ex: Na semana 4, já tinha completado 12 labs no total
labs_completos = [2, 5, 8, 12, 15, 20, 24, 28, 32, 38, 45, 52]

# ============================================================================
# CRIAR FIGURA (GRÁFICO)
# ============================================================================

# Figure() cria um objeto de gráfico vazio
# É como uma tela em branco onde vamos desenhar
fig = go.Figure()

# ============================================================================
# ADICIONAR LINHA NO GRÁFICO
# ============================================================================

# add_trace() adiciona um elemento visual ao gráfico
# Scatter() cria pontos que podem ser conectados por linhas
fig.add_trace(go.Scatter(
    x=semanas,                           # Dados do eixo X (horizontal)
    y=labs_completos,                    # Dados do eixo Y (vertical)
    mode='lines+markers',                # Desenha linha + pontos visíveis
    name='Labs Completos',               # Nome que aparece na legenda
    line=dict(
        color='#667eea',               # Cor da linha (roxo/azul)
        width=3                          # Espessura da linha (pixels)
    ),
    marker=dict(
        size=10,                         # Tamanho dos pontos
        color='#667eea'                # Cor dos pontos (mesma da linha)
    )
))

# ============================================================================
# CONFIGURAR APARÊNCIA DO GRÁFICO
# ============================================================================

# update_layout() personaliza títulos, eixos, tamanho, etc
fig.update_layout(
    title='Progresso de Labs CCNP - 12 Semanas',   # Título principal do gráfico
    xaxis_title='Semana',                          # Título do eixo X
    yaxis_title='Total de Labs Completos',         # Título do eixo Y
    hovermode='x unified',                         # Tooltip mostra todos os valores de um X
    template='plotly_white',                       # Tema visual (fundo branco)
    height=500                                     # Altura do gráfico em pixels
)

# ============================================================================
# EXPORTAR PARA HTML
# ============================================================================

# write_html() salva o gráfico como página web interativa
# Pode abrir no navegador e interagir (zoom, hover, etc)
fig.write_html('../../docs/01_line_chart.html')

# Mensagem de confirmação no terminal
print("✅ Gráfico salvo em: docs/01_line_chart.html")

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Instale as dependências:
   pip install plotly

2. Execute o script:
   python src/basics/01_line_chart_commented.py

3. Abra o arquivo gerado:
   docs/01_line_chart.html no navegador

4. Experimente modificar:
   - Mude os valores em 'labs_completos'
   - Troque a cor para '#43e97b' (verde)
   - Aumente 'width' da linha para 5
   - Mude 'mode' para apenas 'lines' (sem pontos)
   
5. Execute novamente para ver as mudanças!
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ Importar bibliotecas (import)
✅ Criar listas de dados
✅ Criar objeto Figure do Plotly
✅ Adicionar traces (elementos visuais)
✅ Configurar layout (aparência)
✅ Exportar gráfico para HTML
✅ Personalizar cores, tamanhos e estilos
"""