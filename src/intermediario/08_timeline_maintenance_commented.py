#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico Timeline - Janelas de Manutenção (VERSÃO DIDÁTICA)

Visualiza planejamento de manutenções preventivas em dispositivos de rede.
Esta versão contém comentários linha a linha para aprendizado.

Autor: Alexandre Lavorenti Cancilieri
Data: 2025-10-20
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import plotly.figure_factory as ff           # figure_factory para Gantt charts
from datetime import datetime, timedelta     # Manipulação de datas
import random                                # Números aleatórios

# IMPORTANTE: Usamos figure_factory (ff) ao invés de graph_objects
# porque ele tem função específica para criar Gantt charts (timelines)

# ============================================================================
# CONFIGURAÇÃO DE REPRODUTIBILIDADE
# ============================================================================

# Seed para gerar sempre os mesmos dados aleatórios
random.seed(42)

# ============================================================================
# DEFINIR TIPOS DE MANUTENÇÃO E CORES
# ============================================================================

# Dicionário mapeando tipo de manutenção → cor
# Cada tipo tem uma cor específica para fácil identificação visual
tipos_manutencao = {
    'Upgrade Firmware': '#3498db',      # Azul (atualização crítica)
    'Backup Config': '#2ecc71',         # Verde (procedimento seguro)
    'Análise Performance': '#f39c12',   # Laranja (análise/monitoramento)
    'Manutenção Preventiva': '#9b59b6', # Roxo (manutenção programada)
    'Substituição HW': '#e74c3c'        # Vermelho (mudança física)
}

# ============================================================================
# DEFINIR DISPOSITIVOS A SEREM MANTIDOS
# ============================================================================

# Lista de 10 dispositivos críticos da infraestrutura
# Hierarquia típica: Core → Distribution → Access + Firewall + Load Balancer
dispositivos = [
    'RTR-CORE-01',      # Roteador Core (principal)
    'RTR-EDGE-01',      # Roteador de Borda
    'SW-CORE-01',       # Switch Core
    'SW-DIST-01',       # Switch Distribuição 1
    'SW-DIST-02',       # Switch Distribuição 2
    'SW-ACCESS-01',     # Switch Acesso 1
    'FW-01',            # Firewall 1
    'FW-02',            # Firewall 2 (redundância)
    'LB-01',            # Load Balancer 1
    'LB-02'             # Load Balancer 2 (redundância)
]

# ============================================================================
# GERAR DADOS DE MANUTENÇÕES
# ============================================================================

# Lista para armazenar todas as manutenções
manutencoes = []

# Data de referência: hoje
data_inicio = datetime.now()

# Iterar sobre cada dispositivo
# enumerate() retorna (índice, valor)
for i, dispositivo in enumerate(dispositivos):
    # ========================================================================
    # Cada dispositivo terá 2-3 manutenções nos próximos 90 dias
    # ========================================================================
    num_manutencoes = random.randint(2, 3)
    
    # Criar as manutenções para este dispositivo
    for j in range(num_manutencoes):
        # ====================================================================
        # CALCULAR DATA DA MANUTENÇÃO
        # ====================================================================
        
        # Distribuir manutenções ao longo de 90 dias
        # i*7 = começar depois, evitando sobrecarga no início
        # Ex: dispositivo 0 = dias 0-90, dispositivo 1 = dias 7-90, etc
        dias_offset = random.randint(i*7, 90)
        
        # Data de início = hoje + offset de dias
        inicio = data_inicio + timedelta(days=dias_offset)
        
        # ====================================================================
        # CALCULAR DURAÇÃO DA MANUTENÇÃO
        # ====================================================================
        
        # Duração aleatória entre 2 e 8 horas
        # Manutenções típicas:
        # - Backup: 2-3h
        # - Upgrade: 4-6h
        # - Substituição HW: 6-8h
        duracao_horas = random.randint(2, 8)
        
        # Data de fim = início + duração
        fim = inicio + timedelta(hours=duracao_horas)
        
        # ====================================================================
        # ESCOLHER TIPO DE MANUTENÇÃO
        # ====================================================================
        
        # Escolher tipo aleatoriamente da lista de tipos disponíveis
        # list(dict.keys()) = ['Upgrade Firmware', 'Backup Config', ...]
        tipo = random.choice(list(tipos_manutencao.keys()))
        
        # ====================================================================
        # ADICIONAR MANUTENÇÃO À LISTA
        # ====================================================================
        
        # Criar dicionário com informações da manutenção
        # Formato específico para create_gantt():
        manutencoes.append(dict(
            Task=dispositivo,                   # Nome da tarefa (dispositivo)
            Start=inicio,                       # Data/hora de início
            Finish=fim,                         # Data/hora de fim
            Resource=tipo,                      # Tipo/categoria (para cores)
            Description=f'{tipo} - {duracao_horas}h'  # Descrição para hover
        ))

# Resultado: lista com ~25-30 manutenções (10 dispositivos × 2-3 cada)

# ============================================================================
# CRIAR GRÁFICO GANTT (TIMELINE)
# ============================================================================

# create_gantt() é função especial para criar cronogramas/timelines
fig = ff.create_gantt(
    manutencoes,                                # Dados das tarefas
    
    colors=tipos_manutencao,                    # Dicionário tipo → cor
                                                # Cada tipo terá sua cor definida
    
    index_col='Resource',                       # Coluna para agrupar por cor
                                                # Agrupa por 'tipo de manutenção'
    
    show_colorbar=True,                         # Mostrar legenda de cores
    
    group_tasks=True,                           # Agrupar tarefas do mesmo dispositivo
                                                # Coloca todas do mesmo dispositivo juntas
    
    showgrid_x=True,                            # Mostrar grade vertical (datas)
    showgrid_y=True,                            # Mostrar grade horizontal (dispositivos)
    
    title='📅 Cronograma de Manutenções - Próximos 90 Dias',
                                                # Título do gráfico
    
    bar_width=0.3,                              # Largura das barras (0-1)
                                                # 0.3 = barras finas, mais espaço
    
    height=600                                  # Altura do gráfico em pixels
)

# ============================================================================
# CUSTOMIZAR LAYOUT
# ============================================================================

# update_layout() personaliza aparência do gráfico
fig.update_layout(
    # Configuração do eixo X (datas)
    xaxis=dict(
        title='Data',                           # Título do eixo
        gridcolor='rgba(128,128,128,0.2)',      # Cor da grade (cinza transparente)
        showgrid=True                           # Mostrar grade
    ),
    
    # Configuração do eixo Y (dispositivos)
    yaxis=dict(
        title='Dispositivos',                   # Título do eixo
        gridcolor='rgba(128,128,128,0.2)',      # Cor da grade
        showgrid=True                           # Mostrar grade
    ),
    
    plot_bgcolor='white',                       # Fundo branco
    paper_bgcolor='white',                      # Fundo da página branco
    font=dict(family='Arial', size=12),         # Fonte padrão
    hovermode='closest'                         # Hover no elemento mais próximo
)

# ============================================================================
# CUSTOMIZAR TOOLTIP (HOVER)
# ============================================================================

# update_traces() modifica as barras do Gantt
# Customiza o que aparece ao passar o mouse
fig.update_traces(
    hovertemplate=(
        '<b>%{y}</b><br>' +                     # Nome do dispositivo em negrito
        'Início: %{base|%d/%m %H:%M}<br>' +     # Data/hora início formatada
        'Fim: %{x|%d/%m %H:%M}<br>' +           # Data/hora fim formatada
        '<extra></extra>'                       # Remove informação extra
    )
)

# Formatação de datas:
# %d = dia (01-31)
# %m = mês (01-12)
# %H = hora (00-23)
# %M = minuto (00-59)

# ============================================================================
# EXPORTAR PARA HTML
# ============================================================================

# Salvar como página HTML interativa
fig.write_html('../../docs/08_timeline_maintenance.html')

# Mensagem de confirmação
print("✅ Timeline salvo em: docs/08_timeline_maintenance.html")

# ============================================================================
# EXIBIR ESTATÍSTICAS NO TERMINAL
# ============================================================================

print(f"\n📊 Resumo do Planejamento:")

# Período coberto
print(f"📅 Período: {data_inicio.strftime('%d/%m/%Y')} a {(data_inicio + timedelta(days=90)).strftime('%d/%m/%Y')}")

# Total de manutenções
print(f"🔧 Total de manutenções: {len(manutencoes)}")

# Número de dispositivos
print(f"🖥️  Dispositivos: {len(dispositivos)}")

# Contar manutenções por tipo
print(f"\n📋 Por tipo:")
for tipo in tipos_manutencao.keys():
    # sum() com generator expression conta quantas manutenções são deste tipo
    count = sum(1 for m in manutencoes if m['Resource'] == tipo)
    print(f"  {tipo}: {count}")

# Exemplo de saída:
# 📋 Por tipo:
#   Upgrade Firmware: 6
#   Backup Config: 5
#   Análise Performance: 7
#   Manutenção Preventiva: 4
#   Substituição HW: 3

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Certifique-se de ter Plotly instalado:
   pip install plotly

2. Execute o script:
   python src/intermediario/08_timeline_maintenance_commented.py

3. Abra o arquivo gerado:
   docs/08_timeline_maintenance.html no navegador

4. Interaja com a timeline:
   - Visualize todas as manutenções ao longo de 90 dias
   - Passe o mouse sobre barras para ver detalhes
   - Identifique períodos de alta concentração de manutenções
   - Compare tipos de manutenção por cor
   - Use zoom para focar em períodos específicos

5. Experimente modificar:
   - Altere random.seed(42) para novos dados
   - Mude período de 90 para 180 dias
   - Adicione mais dispositivos
   - Crie novos tipos de manutenção
   - Ajuste durações (2-8h para 1-24h)
   - Mude cores dos tipos
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ Criar gráfico Gantt (timeline/cronograma)
✅ Usar plotly.figure_factory ao invés de graph_objects
✅ Trabalhar com datetime e timedelta
✅ Calcular datas futuras com offset
✅ Agrupar tarefas por dispositivo (group_tasks)
✅ Colorir por categoria (index_col='Resource')
✅ Customizar tooltips com formatação de data
✅ Mostrar grade temporal e de tarefas
✅ Calcular estatísticas de cronograma

DIFERENÇAS DOS GRÁFICOS ANTERIORES:
- Linha/Barras: valores discretos
- Scatter: correlação entre variáveis
- Heatmap: matriz de intensidades
- Gauge: valor atual vs meta
- Timeline: duração de eventos ao longo do tempo ← NOVO

QUANDO USAR TIMELINE/GANTT:
✅ Planejamento de projetos
✅ Cronograma de manutenções
✅ Janelas de mudança (change windows)
✅ Disponibilidade de recursos
✅ Upgrades programados
✅ Análise de ocupação temporal

APLICAÇÕES EM REDES:
- Janelas de manutenção (este exemplo)
- Upgrades de firmware programados
- Períodos de backup
- Janelas de mudança (change management)
- Disponibilidade de links/redundância
- Timeline de incidentes
- Cronograma de expansão de rede
"""

# ============================================================================
# VARIAÇÕES POSSÍVEIS
# ============================================================================
"""
TIMELINE SIMPLES (SEM CORES):
fig = ff.create_gantt(manutencoes, showgrid_x=True, showgrid_y=True)

AGRUPAR POR TIPO (ao invés de dispositivo):
# Trocar Task e Resource:
manutencoes.append(dict(
    Task=tipo,          # Tipo no eixo Y
    Resource=dispositivo # Dispositivo como categoria
))

ADICIONAR MARCOS (MILESTONES):
# Adicionar tarefas com duração zero:
manutencoes.append(dict(
    Task='Marco Crítico',
    Start=datetime(2025, 11, 1),
    Finish=datetime(2025, 11, 1),  # Mesma data = marco
    Resource='Milestone'
))

CORES PERSONALIZADAS POR TAREFA:
# Ao invés de cores por tipo, definir cor individual:
manutencoes.append(dict(
    Task=dispositivo,
    Start=inicio,
    Finish=fim,
    Complete={'width': 0.5, 'color': '#FF6B6B'}  # Cor específica
))

ADICIONAR DEPENDÊNCIAS:
# Mostrar que uma tarefa depende de outra:
# (Requer processamento manual com shapes/annotations)

MÚLTIPLAS BARRAS POR LINHA:
# Automático quando group_tasks=True
# Múltiplas manutenções do mesmo dispositivo aparecem na mesma linha
"""