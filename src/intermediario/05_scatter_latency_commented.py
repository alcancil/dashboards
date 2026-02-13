#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico Scatter - Análise de Latência vs Perda de Pacotes (VERSÃO DIDÁTICA)

Correlaciona latência e perda de pacotes em diferentes tipos de links.
Esta versão contém comentários linha a linha para aprendizado.

Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-20
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import plotly.graph_objects as go              # Biblioteca para criar gráficos
import random                                  # Geração de números aleatórios

# ============================================================================
# CONFIGURAÇÃO DE REPRODUTIBILIDADE
# ============================================================================

# Seed para gerar sempre os mesmos dados aleatórios
# Útil para testes e documentação
# Sem seed, cada execução geraria dados diferentes
random.seed(42)

# ============================================================================
# DEFINIÇÃO DE TIPOS DE LINKS E CORES
# ============================================================================

# Lista de tipos de links que vamos simular
tipos_link = ['Fibra', 'Wireless', 'MPLS', 'Internet']

# Dicionário mapeando tipo de link → cor
# Cores escolhidas baseadas em características esperadas:
cores_tipos = {
    'Fibra': '#00CC96',      # Verde - melhor performance (baixa latência/perda)
    'Wireless': '#FFA15A',   # Laranja - performance média (mais variável)
    'MPLS': '#636EFA',       # Azul - corporativo (performance controlada)
    'Internet': '#EF553B'    # Vermelho - mais variável (pior performance)
}

# ============================================================================
# GERAÇÃO DE DADOS SIMULADOS
# ============================================================================

# Lista para armazenar todos os links
links_data = []

# Gerar 50 links com características diferentes
for i in range(50):
    # Escolher tipo de link aleatoriamente
    tipo = random.choice(tipos_link)
    
    # Simular características REALISTAS por tipo de link
    # Cada tipo tem faixas diferentes de latência, perda e tráfego
    
    if tipo == 'Fibra':
        # Fibra óptica: melhor performance
        latencia = random.uniform(5, 30)        # 5-30ms (muito baixa)
        perda = random.uniform(0, 1)            # 0-1% (quase zero)
        trafego = random.uniform(100, 500)      # 100-500 Mbps (alta capacidade)
        
    elif tipo == 'Wireless':
        # Wireless: performance média, mais variável
        latencia = random.uniform(15, 80)       # 15-80ms (média)
        perda = random.uniform(0.5, 5)          # 0.5-5% (moderada)
        trafego = random.uniform(20, 200)       # 20-200 Mbps (limitada)
        
    elif tipo == 'MPLS':
        # MPLS: corporativo, controlado
        latencia = random.uniform(10, 50)       # 10-50ms (controlada)
        perda = random.uniform(0, 2)            # 0-2% (baixa)
        trafego = random.uniform(50, 300)       # 50-300 Mbps (média-alta)
        
    else:  # Internet
        # Internet pública: mais variável e imprevisível
        latencia = random.uniform(30, 150)      # 30-150ms (alta variação)
        perda = random.uniform(1, 8)            # 1-8% (pode ser alta)
        trafego = random.uniform(10, 150)       # 10-150 Mbps (limitada)
    
    # Adicionar link à lista com dados arredondados
    links_data.append({
        'nome': f'Link-{i+1:02d}',              # Nome: Link-01, Link-02, etc
        'tipo': tipo,                            # Tipo do link
        'latencia_ms': round(latencia, 2),       # Latência em milissegundos
        'perda_pacotes': round(perda, 2),        # Perda em percentual
        'trafego_mbps': round(trafego, 2)        # Tráfego em Mbps
    })

# ============================================================================
# CRIAR FIGURA DO GRÁFICO
# ============================================================================

# Figure() cria um objeto de gráfico vazio
fig = go.Figure()

# ============================================================================
# ADICIONAR SCATTER PLOTS (um para cada tipo de link)
# ============================================================================

# Iterar sobre cada tipo de link para criar um trace separado
# Isso permite legendas e cores diferentes por tipo
for tipo in tipos_link:
    # Filtrar apenas links do tipo atual
    # List comprehension: percorre links_data e mantém apenas os que têm este tipo
    links_tipo = [link for link in links_data if link['tipo'] == tipo]
    
    # Adicionar trace (camada de dados) ao gráfico
    fig.add_trace(go.Scatter(
        # Eixo X: lista de latências de todos os links deste tipo
        # List comprehension extrai apenas o campo 'latencia_ms'
        x=[link['latencia_ms'] for link in links_tipo],
        
        # Eixo Y: lista de perdas de pacotes
        y=[link['perda_pacotes'] for link in links_tipo],
        
        mode='markers',                          # Modo: apenas marcadores (pontos)
                                                # 'lines' = linhas
                                                # 'lines+markers' = ambos
        
        name=tipo,                              # Nome que aparece na legenda
        
        marker=dict(
            # Tamanho proporcional ao tráfego
            # Dividir por 10 para não ficar muito grande
            # Link com 500 Mbps = tamanho 50 pixels
            size=[link['trafego_mbps'] / 10 for link in links_tipo],
            
            color=cores_tipos[tipo],            # Cor específica do tipo
            
            opacity=0.7,                        # Transparência (0=invisível, 1=opaco)
                                                # 0.7 permite ver sobreposições
            
            line=dict(
                color='white',                  # Borda branca nos pontos
                width=1                         # Espessura da borda
            )
        ),
        
        # Texto que aparece ao passar mouse (hover)
        # Criar lista de textos customizados para cada ponto
        text=[f"{link['nome']}<br>Tráfego: {link['trafego_mbps']} Mbps" 
              for link in links_tipo],
        
        # Template do hover (tooltip)
        # %{text} = texto definido acima
        # %{x} = valor do eixo X (latência)
        # %{y} = valor do eixo Y (perda)
        # <extra></extra> = remove nome do trace do tooltip
        hovertemplate=(
            '<b>%{text}</b><br>' +              # Nome do link em negrito
            'Latência: %{x} ms<br>' +           # Latência
            'Perda: %{y}%<br>' +                # Perda de pacotes
            '<extra></extra>'                   # Remove informação extra
        )
    ))

# ============================================================================
# CONFIGURAR LAYOUT DO GRÁFICO
# ============================================================================

fig.update_layout(
    title='Análise de Performance de Links de Rede',
                                                # Título principal
    
    # Configuração do eixo X (horizontal)
    xaxis=dict(
        title='Latência (ms)',                  # Título do eixo
        gridcolor='rgba(128,128,128,0.2)',      # Cor da grade (cinza transparente)
        showgrid=True,                          # Mostrar linhas de grade
        zeroline=False                          # Não mostrar linha no zero
    ),
    
    # Configuração do eixo Y (vertical)
    yaxis=dict(
        title='Perda de Pacotes (%)',          # Título do eixo
        gridcolor='rgba(128,128,128,0.2)',      # Cor da grade
        showgrid=True,                          # Mostrar linhas de grade
        zeroline=False                          # Não mostrar linha no zero
    ),
    
    plot_bgcolor='#F8F9FA',                     # Cor de fundo do gráfico (cinza claro)
    paper_bgcolor='white',                      # Cor de fundo da página (branco)
    font=dict(family='Arial', size=12),         # Fonte padrão
    
    hovermode='closest',                        # Modo de hover: ponto mais próximo
                                                # Outras opções: 'x', 'y', False
    
    showlegend=True,                            # Mostrar legenda
    
    # Configuração da legenda
    legend=dict(
        title='Tipo de Link',                   # Título da legenda
        orientation='v',                        # Orientação vertical
        yanchor='top',                          # Âncora vertical (topo)
        y=1,                                    # Posição Y (1 = topo)
        xanchor='left',                         # Âncora horizontal (esquerda)
        x=1.02                                  # Posição X (1.02 = à direita do gráfico)
    ),
    
    height=600                                  # Altura do gráfico em pixels
)

# ============================================================================
# ADICIONAR ZONA DE PERFORMANCE ÓTIMA (VISUAL)
# ============================================================================

# add_shape() adiciona formas geométricas ao gráfico
# Retângulo verde semi-transparente indicando "zona ótima"
fig.add_shape(
    type="rect",                                # Tipo: retângulo
    x0=0, x1=50,                                # Coordenadas X (0 a 50ms de latência)
    y0=0, y1=2,                                 # Coordenadas Y (0 a 2% de perda)
    fillcolor="green",                          # Cor de preenchimento
    opacity=0.1,                                # Transparência (10% = muito leve)
    layer="below",                              # Desenhar abaixo dos pontos
    line_width=0                                # Sem borda
)

# Adicionar texto dentro da zona ótima
fig.add_annotation(
    x=25,                                       # Posição X (centro da zona)
    y=1,                                        # Posição Y (centro da zona)
    text="Zona Ótima",                          # Texto a exibir
    showarrow=False,                            # Não mostrar seta
    font=dict(size=10, color='green'),          # Fonte pequena e verde
    opacity=0.5                                 # Texto semi-transparente
)

# ============================================================================
# EXPORTAR PARA HTML
# ============================================================================

# Salvar como página HTML interativa
# ../../ = sobe 2 níveis (de src/intermediario/ para raiz)
fig.write_html('../../docs/05_scatter_latency.html')

# Mensagens de confirmação
print("✅ Gráfico salvo em: docs/05_scatter_latency.html")
print(f"📊 Total de links analisados: {len(links_data)}")
print(f"🔍 Tipos de link: {', '.join(tipos_link)}")

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Certifique-se de ter Plotly instalado:
   pip install plotly

2. Execute o script:
   python src/intermediario/05_scatter_latency_commented.py

3. Abra o arquivo gerado:
   docs/05_scatter_latency.html no navegador

4. Interaja com o gráfico:
   - Passe o mouse sobre pontos para ver detalhes
   - Clique na legenda para ocultar/mostrar tipos de link
   - Use zoom (clicar e arrastar)
   - Duplo clique para resetar

5. Experimente modificar:
   - Altere random.seed(42) para gerar dados diferentes
   - Mude as faixas de latência/perda por tipo
   - Adicione mais tipos de link
   - Altere cores em cores_tipos
   - Mude tamanho dos pontos (trafego_mbps / X)
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ Criar gráfico de dispersão (scatter plot)
✅ Usar cores diferentes por categoria
✅ Tamanho dinâmico de marcadores (proporcional a variável)
✅ Filtrar dados com list comprehension
✅ Adicionar formas geométricas (add_shape)
✅ Adicionar anotações de texto (add_annotation)
✅ Customizar tooltips com hovertemplate
✅ Simular dados realistas por categoria
✅ Usar random.seed() para reprodutibilidade
✅ Iterar sobre categorias para criar múltiplos traces

DIFERENÇAS DOS GRÁFICOS ANTERIORES:
- Linha: mostra evolução temporal (1 variável ao longo do tempo)
- Barras: compara categorias (valores discretos)
- Pizza: mostra proporções (partes de um todo)
- Scatter: correlaciona 2 variáveis (X vs Y) ← NOVO

QUANDO USAR SCATTER:
✅ Analisar correlação entre duas métricas
✅ Identificar padrões e outliers
✅ Comparar performance entre grupos
✅ Troubleshooting de rede (latência vs perda)
✅ Análise de capacidade (uso vs disponível)

APLICAÇÕES EM REDES:
- Latência vs Perda de Pacotes (este exemplo)
- Throughput vs Utilização de CPU
- Número de Conexões vs Tempo de Resposta
- Largura de Banda vs Jitter
- Distância vs Latência
"""

# ============================================================================
# VARIAÇÕES POSSÍVEIS
# ============================================================================
"""
ADICIONAR LINHA DE TENDÊNCIA:
import numpy as np
from scipy import stats

x = [link['latencia_ms'] for link in links_data]
y = [link['perda_pacotes'] for link in links_data]
slope, intercept, r, p, se = stats.linregress(x, y)
line_x = np.linspace(min(x), max(x), 100)
line_y = slope * line_x + intercept

fig.add_trace(go.Scatter(
    x=line_x, y=line_y,
    mode='lines',
    name='Tendência',
    line=dict(dash='dash', color='red')
))

USAR ESCALA LOGARÍTMICA:
fig.update_xaxes(type="log")
fig.update_yaxes(type="log")

ADICIONAR MAIS ZONAS:
# Zona de Atenção (amarela)
fig.add_shape(
    type="rect",
    x0=50, x1=100, y0=2, y1=5,
    fillcolor="yellow",
    opacity=0.1,
    layer="below",
    line_width=0
)

# Zona Crítica (vermelha)
fig.add_shape(
    type="rect",
    x0=100, x1=200, y0=5, y1=10,
    fillcolor="red",
    opacity=0.1,
    layer="below",
    line_width=0
)

COLORIR POR FAIXA DE VALORES:
cores_customizadas = []
for link in links_data:
    if link['perda_pacotes'] < 1:
        cores_customizadas.append('green')
    elif link['perda_pacotes'] < 3:
        cores_customizadas.append('yellow')
    else:
        cores_customizadas.append('red')

marker=dict(color=cores_customizadas, ...)
"""