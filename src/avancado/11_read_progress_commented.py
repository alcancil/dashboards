#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leitura e Métricas do Progresso CCNP (VERSÃO DIDÁTICA)

Lê o arquivo data/ccnp_progress.json, calcula métricas por domínio
e exibe resumo no terminal. Serve como módulo base para os dashboards.
Esta versão contém comentários linha a linha para aprendizado.

Autor: Alexandre Lavorenti Cancilieri
Data: 2026-02-22
"""

# ============================================================================
# IMPORTAÇÕES
# ============================================================================

import json       # Módulo nativo do Python para ler e escrever arquivos JSON
                  # Não precisa instalar — já vem com o Python

from datetime import datetime   # Classe para trabalhar com datas e horas
                                # Usada para calcular dias restantes até a meta

from pathlib import Path  # Classe moderna para manipulação de caminhos
                          # Substitui os.path (mais legível, segura e orientada a objetos)
                          # Permite montar caminhos usando o operador "/"

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]
# Path(__file__)        → caminho do arquivo atual
# .resolve()            → converte para caminho absoluto
# .parents[2]           → sobe dois níveis na hierarquia de pastas
# Resultado: pasta raiz do projeto (DASHBOARDS)

DATA_DIR = BASE_DIR / "data" / "processed"
# Operador "/" do Path junta partes do caminho
# Equivale a: BASE_DIR/data/processed
# Vantagem: funciona em Windows, Linux e Mac automaticamente

CAMINHO_JSON = DATA_DIR / "ccnp_progress.json"
# Caminho final completo até o arquivo JSON
# Agora o arquivo está em: data/processed/ccnp_progress.json

# ============================================================================
# FUNÇÕES DE LEITURA E CÁLCULO
# ============================================================================

def carregar_dados(caminho=CAMINHO_JSON):
    """
    Abre o arquivo JSON e retorna o conteúdo como dicionário Python.
    Parâmetro caminho tem valor padrão = CAMINHO_JSON definido acima,
    mas pode ser sobrescrito passando outro caminho (útil para testes).
    """
    with open(caminho, 'r', encoding='utf-8') as f:   # Abre o arquivo em modo leitura ('r')
                                                       # encoding='utf-8' para caracteres especiais (ã, ç, etc.)
        return json.load(f)   # json.load() converte o texto JSON em dicionário Python
                              # Ex: {"nome": "QoS"} → {'nome': 'QoS'}


def calcular_metricas_topico(topico):
    """
    Recebe um dicionário de tópico (do JSON) e retorna um novo dicionário
    com todos os campos calculados: totais, concluídos e percentual.
    """

    # .get('teoria', {}) → acessa a chave 'teoria' do dicionário
    # Se a chave não existir (tópico sem teoria), retorna {} (dict vazio)
    # Isso evita KeyError quando o tópico não tem teoria/labs/resumo
    teoria  = topico.get('teoria', {})
    labs    = topico.get('labs',   {})
    resumo  = topico.get('resumo', {})

    # Somar totais e concluídos dos três tipos de atividade
    # .get('total', 0) → se a chave 'total' não existir, usa 0 como padrão
    total      = (teoria.get('total', 0) +
                  labs.get('total', 0)   +
                  resumo.get('total', 0))

    concluidos = (teoria.get('concluidos', 0) +
                  labs.get('concluidos', 0)   +
                  resumo.get('concluidos', 0))

    # Calcular percentual com proteção contra divisão por zero
    # 'if total > 0 else 0.0' → se total for 0 (tópico vazio), retorna 0.0
    percentual = round((concluidos / total * 100), 1) if total > 0 else 0.0

    # Retornar dicionário com todos os campos calculados
    # Esse dicionário será usado pelas funções seguintes e pelos dashboards
    return {
        'nome':         topico['nome'],              # Nome do tópico (ex: 'QoS')
        'teoria_total': teoria.get('total', 0),      # Qtd total de aulas de teoria
        'teoria_ok':    teoria.get('concluidos', 0), # Qtd de aulas concluídas
        'labs_total':   labs.get('total', 0),        # Qtd total de laboratórios
        'labs_ok':      labs.get('concluidos', 0),   # Qtd de labs concluídos
        'resumo_total': resumo.get('total', 0),      # Qtd total de resumos
        'resumo_ok':    resumo.get('concluidos', 0), # Qtd de resumos concluídos
        'total':        total,                       # Total geral de itens
        'concluidos':   concluidos,                  # Total geral concluído
        'percentual':   percentual,                  # % de conclusão do tópico
    }


def calcular_metricas_dominio(dominio):
    """
    Recebe um dicionário de domínio (do JSON) e retorna métricas agregadas
    de todos os tópicos dentro dele.
    """

    topicos = dominio.get('topicos', [])   # Lista de tópicos do domínio
                                           # Se 'topicos' não existir, retorna lista vazia []

    # Contadores zerados para acumular os valores de todos os tópicos
    teoria_total = labs_total = resumo_total = 0   # Totais planejados
    teoria_ok    = labs_ok    = resumo_ok    = 0   # Totais concluídos

    metricas_topicos = []   # Lista que vai acumular as métricas de cada tópico

    for topico in topicos:                      # Itera sobre cada tópico do domínio
        m = calcular_metricas_topico(topico)    # Calcula métricas do tópico individualmente
        metricas_topicos.append(m)              # Adiciona à lista de métricas

        # Acumular valores nos contadores do domínio
        teoria_total += m['teoria_total'];  teoria_ok += m['teoria_ok']
        labs_total   += m['labs_total'];    labs_ok   += m['labs_ok']
        resumo_total += m['resumo_total'];  resumo_ok += m['resumo_ok']

    # Calcular totais e percentual do domínio inteiro
    total      = teoria_total + labs_total + resumo_total
    concluidos = teoria_ok    + labs_ok    + resumo_ok
    percentual = round((concluidos / total * 100), 1) if total > 0 else 0.0

    return {
        'id':           dominio['id'],       # Ex: '01', '02', etc.
        'nome':         dominio['nome'],     # Ex: 'Architecture'
        'teoria_total': teoria_total,        # Total de teoria no domínio
        'teoria_ok':    teoria_ok,           # Teoria concluída no domínio
        'labs_total':   labs_total,          # Total de labs no domínio
        'labs_ok':      labs_ok,             # Labs concluídos no domínio
        'resumo_total': resumo_total,        # Total de resumos no domínio
        'resumo_ok':    resumo_ok,           # Resumos concluídos no domínio
        'total':        total,               # Total geral do domínio
        'concluidos':   concluidos,          # Total concluído no domínio
        'percentual':   percentual,          # % de conclusão do domínio
        'topicos':      metricas_topicos,    # Lista com métricas de cada tópico
        'iniciado':     total > 0,           # True se o domínio tem pelo menos 1 item
                                             # False para Network Assurance e Security (vazios)
    }


def calcular_metricas_gerais(dados):
    """
    Função principal de cálculo. Recebe o dicionário completo do JSON
    e retorna um dicionário com todas as métricas consolidadas.
    Este é o dicionário que os dashboards vão consumir.
    """

    # Calcular métricas de todos os domínios de uma vez
    # List comprehension: equivale a um for loop que monta uma lista
    dominios_metricas = [calcular_metricas_dominio(d) for d in dados['dominios']]

    # Somar métricas de todos os domínios para obter os totais gerais
    # sum() com generator expression: soma um campo específico de cada domínio
    teoria_total = sum(d['teoria_total'] for d in dominios_metricas)
    teoria_ok    = sum(d['teoria_ok']    for d in dominios_metricas)
    labs_total   = sum(d['labs_total']   for d in dominios_metricas)
    labs_ok      = sum(d['labs_ok']      for d in dominios_metricas)
    resumo_total = sum(d['resumo_total'] for d in dominios_metricas)
    resumo_ok    = sum(d['resumo_ok']    for d in dominios_metricas)

    # Totais gerais do repositório
    total      = teoria_total + labs_total + resumo_total
    concluidos = teoria_ok    + labs_ok    + resumo_ok
    percentual = round((concluidos / total * 100), 1) if total > 0 else 0.0

    # Calcular dias restantes até a meta de conclusão
    # datetime.strptime() → converte string de data para objeto datetime
    # '%Y-%m-%d' → formato esperado: '2026-12-31'
    meta  = datetime.strptime(dados['meta_conclusao'], '%Y-%m-%d')
    hoje  = datetime.now()                  # Data e hora atuais do sistema
    dias_restantes = (meta - hoje).days     # Subtração de datas → timedelta
                                            # .days → extrai só os dias inteiros

    # Retornar dicionário completo com todos os dados para o dashboard
    return {
        'repositorio':    dados['repositorio'],        # Nome do repositório
        'ultima_att':     dados['ultima_atualizacao'], # Data da última atualização
        'meta_conclusao': dados['meta_conclusao'],     # Data meta de conclusão
        'dias_restantes': dias_restantes,              # Dias até a meta
        'teoria_total':   teoria_total,                # Total de teoria (todos domínios)
        'teoria_ok':      teoria_ok,                   # Teoria concluída (todos domínios)
        'labs_total':     labs_total,                  # Total de labs (todos domínios)
        'labs_ok':        labs_ok,                     # Labs concluídos (todos domínios)
        'resumo_total':   resumo_total,                # Total de resumos (todos domínios)
        'resumo_ok':      resumo_ok,                   # Resumos concluídos (todos domínios)
        'total':          total,                       # Total geral de itens
        'concluidos':     concluidos,                  # Total geral concluído
        'percentual':     percentual,                  # % geral de conclusão
        'dominios':       dominios_metricas,           # Lista com métricas por domínio
    }

# ============================================================================
# FUNÇÕES DE EXIBIÇÃO NO TERMINAL
# ============================================================================

def gerar_barra(percentual, tamanho=20):
    """
    Gera uma barra de progresso visual com caracteres de texto.
    Ex: [████████████░░░░░░░░]  60.0%

    percentual → valor de 0 a 100
    tamanho    → quantidade de caracteres da barra (padrão: 20)
    """
    preenchido = int(percentual / 100 * tamanho)   # Qtd de blocos preenchidos
                                                    # Ex: 60% de 20 = 12 blocos
    vazios     = tamanho - preenchido               # Qtd de blocos vazios

    return '[' + '█' * preenchido + '░' * vazios + ']'
    # '█' * 12 → '████████████'  (parte concluída)
    # '░' * 8  → '░░░░░░░░'     (parte restante)


def exibir_resumo(metricas):
    """
    Exibe o resumo completo de progresso no terminal.
    Recebe o dicionário retornado por calcular_metricas_gerais().
    """
    g = metricas   # Atalho para não repetir 'metricas.' em todo lugar

    # Cabeçalho
    print("=" * 55)
    print(f"  📚 {g['repositorio']}")                                          # Nome do repositório
    print(f"  📅 Atualizado : {g['ultima_att']}")                              # Data da última atualização
    print(f"  🎯 Meta       : {g['meta_conclusao']} ({g['dias_restantes']} dias restantes)")
    print("=" * 55)

    # Iterar sobre cada domínio e exibir suas métricas
    for d in g['dominios']:

        if not d['iniciado']:                                # Domínio sem nenhum item ainda
            print(f"\n⬜ {d['id']} - {d['nome']}  (não iniciado)")
            continue                                         # Pula para o próximo domínio

        # Domínio com itens: exibir barra + detalhes
        barra = gerar_barra(d['percentual'])                 # Gera barra de progresso
        print(f"\n🟢 {d['id']} - {d['nome']}")
        print(f"   {barra}  {d['percentual']}%")            # Barra visual + percentual
        print(f"   Teoria  : {d['teoria_ok']}/{d['teoria_total']}")   # Ex: Teoria : 31/31
        print(f"   Labs    : {d['labs_ok']}/{d['labs_total']}")       # Ex: Labs   : 5/5
        print(f"   Resumo  : {d['resumo_ok']}/{d['resumo_total']}")   # Ex: Resumo : 1/1

    # Rodapé com totais gerais
    print("\n" + "=" * 55)
    barra_geral = gerar_barra(g['percentual'])
    print(f"  PROGRESSO GERAL  {barra_geral}  {g['percentual']}%")
    print(f"  Itens concluídos : {g['concluidos']}/{g['total']}")
    print(f"  Teoria  : {g['teoria_ok']}/{g['teoria_total']}")
    print(f"  Labs    : {g['labs_ok']}/{g['labs_total']}")
    print(f"  Resumo  : {g['resumo_ok']}/{g['resumo_total']}")
    print("=" * 55)

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

# if __name__ == '__main__' → este bloco só executa quando o script é rodado
# diretamente (python 11_read_progress.py).
# Se outro script importar este como módulo (import 11_read_progress),
# este bloco NÃO executa — só as funções ficam disponíveis.
# Isso é o que permite que o script 12 (dashboard) importe as funções
# deste script sem re-executar o terminal.

if __name__ == '__main__':
    dados    = carregar_dados()              # 1. Lê e desserializa o JSON
    metricas = calcular_metricas_gerais(dados)   # 2. Calcula todas as métricas
    exibir_resumo(metricas)                  # 3. Exibe no terminal

# ============================================================================
# COMO USAR ESTE SCRIPT
# ============================================================================
"""
1. Certifique-se de que o arquivo de dados existe:
   dashboards/data/ccnp_progress.json

2. Execute diretamente para ver o resumo no terminal:
   python src/avancado/11_read_progress.py

3. Importe as funções em outro script (ex: 12_dashboard_progress.py):
   import sys, os
   sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
   from 11_read_progress import carregar_dados, calcular_metricas_gerais

4. Atualize o JSON quando concluir novos itens:
   - Abra data/ccnp_progress.json
   - Altere o campo 'concluidos' do tópico correspondente
   - Atualize 'ultima_atualizacao' para a data atual
   - Execute o script novamente para ver o novo resumo
"""

# ============================================================================
# CONCEITOS APRENDIDOS
# ============================================================================
"""
✅ Ler arquivo JSON com json.load()
✅ Montar caminhos portáveis com os.path.join() e os.path.dirname(__file__)
✅ Usar .get() com valor padrão para evitar KeyError em dicionários
✅ Calcular percentual com proteção contra divisão por zero
✅ Agregar dados de listas aninhadas com sum() e generator expression
✅ Converter string de data para datetime com strptime()
✅ Calcular diferença entre datas com subtração de objetos datetime
✅ Separar lógica de dados (funções) de lógica de exibição (exibir_resumo)
✅ Usar if __name__ == '__main__' para permitir importação como módulo
✅ Gerar barra de progresso visual com multiplicação de strings

PADRÃO IMPORTANTE - SEPARAÇÃO DE RESPONSABILIDADES:
Este script tem três camadas distintas:

  1. LEITURA   → carregar_dados()
     Só lê o arquivo. Não calcula nada.

  2. CÁLCULO   → calcular_metricas_topico()
                 calcular_metricas_dominio()
                 calcular_metricas_gerais()
     Só calcula. Não exibe nada, não lê arquivo.

  3. EXIBIÇÃO  → exibir_resumo(), gerar_barra()
     Só exibe no terminal. Não calcula nada.

Por que isso importa?
- O script 12 (dashboard Plotly) vai usar as camadas 1 e 2
  mas vai IGNORAR a camada 3 (vai criar gráficos no lugar)
- Quando vier a API do GitHub (Fase 4), só a camada 1 muda
  (carregar_dados vai chamar a API ao invés de ler o arquivo)
- As camadas 2 e 3 continuam idênticas

FLUXO DE DADOS:
JSON → carregar_dados() → dict Python
     → calcular_metricas_gerais() → dict de métricas
     → exibir_resumo() → saída no terminal
     → (futuro) dashboard_progress() → HTML interativo
"""

# ============================================================================
# VARIAÇÕES POSSÍVEIS
# ============================================================================
"""
CALCULAR VELOCIDADE DE PROGRESSO (labs por semana):
from datetime import timedelta
inicio = datetime(2025, 10, 1)          # Data que começou os estudos
semanas = (datetime.now() - inicio).days / 7
velocidade = metricas['labs_ok'] / semanas
print(f"Ritmo: {velocidade:.1f} labs/semana")

PROJETAR DATA DE CONCLUSÃO:
labs_restantes = metricas['labs_total'] - metricas['labs_ok']
semanas_restantes = labs_restantes / velocidade
conclusao = datetime.now() + timedelta(weeks=semanas_restantes)
print(f"Projeção: {conclusao.strftime('%d/%m/%Y')}")

EXPORTAR MÉTRICAS PARA CSV:
import csv
with open('data/metricas.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['nome','percentual','labs_ok','labs_total'])
    writer.writeheader()
    for d in metricas['dominios']:
        writer.writerow(d)

SALVAR HISTÓRICO DE SNAPSHOTS:
# Guardar o estado atual com timestamp para ver evolução ao longo do tempo
snapshot = {'data': datetime.now().isoformat(), 'metricas': metricas}
with open('data/historico.json', 'a') as f:
    f.write(json.dumps(snapshot) + '\n')
"""