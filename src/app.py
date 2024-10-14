import os
import json
import oracledb
import matplotlib.pyplot as plt
import pandas as pd
import time
import logging
import pickle
import unittest
import connect_db
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict
from queue import PriorityQueue
from connect_db import conectar_banco, fechar_conexao
from sqlalchemy import create_engine
from setup_bd import setup_banco_dados

    
# Configuração de logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Carregamento de variáveis de ambiente
load_dotenv()

# Estabelecer a conexão BD
#conn = conectar_banco()
#if conn:
  #  setup_banco_dados(conn)

# Configuração
class Config:
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_DSN = os.getenv('DB_DSN')

# Classes para representar entidades
@dataclass
class Colheita:
    ano: int
    quantidade_colhida: float

@dataclass
class Clima:
    ano: int
    temperatura_media: float
    precipitacao: float

@dataclass
class MaturidadeCana:
    ano: int
    indice_maturidade: float

@dataclass
class CondicoesSolo:
    ano: int
    ph: float
    nutrientes: float

@dataclass
class DadosCompletos:
    colheita: Colheita
    clima: Clima
    maturidade: MaturidadeCana
    solo: CondicoesSolo

# Classe principal para gerenciamento de dados
class GerenciadorDados:
    def __init__(self):
        self.dados_por_ano: Dict[int, DadosCompletos] = {}
        self.colheitas_agendadas: PriorityQueue = PriorityQueue()
        self.recursos_alocados: set = set()
        self.operacoes_pendentes: List[Dict] = []

    def adicionar_dados(self, dados: DadosCompletos):
        """
        Adiciona novos dados ao gerenciador.

        Args:
        dados (DadosCompletos): Objeto contendo os dados completos de um ano.
        """
        self.dados_por_ano[dados.colheita.ano] = dados
        self.operacoes_pendentes.append({"tipo": "inserir", "dados": asdict(dados)})
        logging.info(f"Dados adicionados para o ano {dados.colheita.ano}")

    def alterar_dados(self, ano: int, campo: str, valor: float):
        """
        Altera dados existentes no gerenciador.

        Args:
        ano (int): Ano dos dados a serem alterados.
        campo (str): Campo a ser alterado.
        valor (float): Novo valor para o campo.
        """
        if ano in self.dados_por_ano:
            dados = self.dados_por_ano[ano]
            if campo == 'quantidade_colhida':
                dados.colheita.quantidade_colhida = valor
            elif campo == 'temperatura_media':
                dados.clima.temperatura_media = valor
            elif campo == 'precipitacao':
                dados.clima.precipitacao = valor
            elif campo == 'indice_maturidade':
                dados.maturidade.indice_maturidade = valor
            elif campo == 'ph':
                dados.solo.ph = valor
            elif campo == 'nutrientes':
                dados.solo.nutrientes = valor
            self.operacoes_pendentes.append({"tipo": "atualizar", "ano": ano, "campo": campo, "valor": valor})
            logging.info(f"Dados alterados para o ano {ano}, campo {campo}")
        else:
            logging.warning(f"Tentativa de alterar dados inexistentes para o ano {ano}")

    def excluir_dados(self, ano: int):
        """
        Exclui dados de um ano específico.

        Args:
        ano (int): Ano dos dados a serem excluídos.
        """
        if ano in self.dados_por_ano:
            del self.dados_por_ano[ano]
            self.operacoes_pendentes.append({"tipo": "excluir", "ano": ano})
            logging.info(f"Dados excluídos para o ano {ano}")
        else:
            logging.warning(f"Tentativa de excluir dados inexistentes para o ano {ano}")

    def agendar_colheita(self, plantacao_id: int, data_colheita: datetime):
        """
        Agenda uma colheita.

        Args:
        plantacao_id (int): ID da plantação.
        data_colheita (datetime): Data agendada para a colheita.
        """
        self.colheitas_agendadas.put((data_colheita, plantacao_id))
        logging.info(f"Colheita agendada para plantação {plantacao_id} em {data_colheita}")

    def alocar_recurso(self, recurso: str):
        """
        Aloca um recurso.

        Args:
        recurso (str): Nome do recurso a ser alocado.
        """
        self.recursos_alocados.add(recurso)
        logging.info(f"Recurso {recurso} alocado")

    def carregar_dados_json(self, arquivo):
        """
        Carrega dados de um arquivo JSON.

        Args:
        arquivo (str): Caminho do arquivo JSON.
        """
        try:
            with open(arquivo, 'r') as f:
                dados_json = json.load(f)
            for dado in dados_json:
                dados_completos = DadosCompletos(
                    colheita=Colheita(ano=dado['ano'], quantidade_colhida=dado['quantidade_colhida']),
                    clima=Clima(ano=dado['ano'], temperatura_media=dado['clima']['temperatura_media'], precipitacao=dado['clima']['precipitacao']),
                    maturidade=MaturidadeCana(ano=dado['ano'], indice_maturidade=dado['maturidade_cana']['indice_maturidade']),
                    solo=CondicoesSolo(ano=dado['ano'], ph=dado['condicoes_solo']['ph'], nutrientes=dado['condicoes_solo']['nutrientes'])
                )
                self.adicionar_dados(dados_completos)
            logging.info(f"Dados carregados do arquivo JSON {arquivo}")
        except Exception as e:
            logging.error(f"Erro ao carregar dados do arquivo JSON {arquivo}: {e}")

    def listar_agendamentos(self):
        """
        Lista todos os agendamentos de colheita.

        Returns:
        List: Lista de tuplas (data_colheita, plantacao_id) ordenada por data.
        """
        agendamentos = list(self.colheitas_agendadas.queue)
        agendamentos.sort(key=lambda x: x[0])
        return agendamentos

    def excluir_todos_dados(self):
        """
        Exclui todos os dados do gerenciador.
        """
        self.dados_por_ano.clear()
        self.operacoes_pendentes.append({"tipo": "excluir_todos"})
        logging.info("Todos os dados foram excluídos")

    def sincronizar_com_banco(self, conn):
        """
        Sincroniza os dados do gerenciador com o banco de dados.

        Args:
        conn: Conexão com o banco de dados.
        """
        cursor = conn.cursor()
        try:
            for operacao in self.operacoes_pendentes:
                if operacao["tipo"] == "inserir":
                    dados = operacao["dados"]
                    cursor.execute("""
                        INSERT INTO Colheita (ano, quantidade_colhida) VALUES (:ano, :quantidade_colhida)
                    """, ano=dados['colheita']['ano'], quantidade_colhida=dados['colheita']['quantidade_colhida'])
                    cursor.execute("""
                        INSERT INTO Clima (ano, temperatura_media, precipitacao) VALUES (:ano, :temperatura_media, :precipitacao)
                    """, ano=dados['clima']['ano'], temperatura_media=dados['clima']['temperatura_media'], precipitacao=dados['clima']['precipitacao'])
                    cursor.execute("""
                        INSERT INTO MaturidadeCana (ano, indice_maturidade) VALUES (:ano, :indice_maturidade)
                    """, ano=dados['maturidade']['ano'], indice_maturidade=dados['maturidade']['indice_maturidade'])
                    cursor.execute("""
                        INSERT INTO CondicoesSolo (ano, ph, nutrientes) VALUES (:ano, :ph, :nutrientes)
                    """, ano=dados['solo']['ano'], ph=dados['solo']['ph'], nutrientes=dados['solo']['nutrientes'])
                elif operacao["tipo"] == "atualizar":
                    tabela = ""
                    if operacao["campo"] == 'quantidade_colhida':
                        tabela = "Colheita"
                    elif operacao["campo"] in ['temperatura_media', 'precipitacao']:
                        tabela = "Clima"
                    elif operacao["campo"] == 'indice_maturidade':
                        tabela = "MaturidadeCana"
                    elif operacao["campo"] in ['ph', 'nutrientes']:
                        tabela = "CondicoesSolo"
                    
                    cursor.execute(f"""
                        UPDATE {tabela} SET {operacao['campo']} = :valor WHERE ano = :ano
                    """, valor=operacao['valor'], ano=operacao['ano'])
                elif operacao["tipo"] == "excluir":
                    for tabela in ["Colheita", "Clima", "MaturidadeCana", "CondicoesSolo"]:
                        cursor.execute(f"DELETE FROM {tabela} WHERE ano = :ano", ano=operacao['ano'])
                elif operacao["tipo"] == "excluir_todos":
                    for tabela in ["Colheita", "Clima", "MaturidadeCana", "CondicoesSolo"]:
                        cursor.execute(f"DELETE FROM {tabela}")
            
            conn.commit()
            self.operacoes_pendentes.clear()
            logging.info("Dados sincronizados com o banco de dados com sucesso")
        except Exception as e:
            conn.rollback()
            logging.error(f"Erro ao sincronizar dados com o banco: {e}")
        finally:
            cursor.close()

# Funções de conexão e manipulação do banco de dados
# def conectar_banco(max_tentativas=3, tempo_espera=5):
#     """
#     Estabelece uma conexão com o banco de dados Oracle.

#     Args:
#     max_tentativas (int): Número máximo de tentativas de conexão.
#     tempo_espera (int): Tempo de espera entre tentativas em segundos.

#     Returns:
#     oracledb.Connection: Objeto de conexão com o banco de dados, ou None se falhar.
#     """
#     for tentativa in range(max_tentativas):
#         try:
#             conn = oracledb.connect(user=Config.DB_USER, password=Config.DB_PASSWORD, dsn=Config.DB_DSN, timeout=30)
#             logging.info("Conectado ao banco de dados")
#             return conn
#         except oracledb.DatabaseError as e:
#             logging.error(f"Tentativa {tentativa + 1} falhou. Erro: {e}")
#             if tentativa < max_tentativas - 1:
#                 logging.info(f"Tentando reconectar em {tempo_espera} segundos...")
#                 time.sleep(tempo_espera)
#             else:
#                 logging.error("Falha ao conectar ao banco de dados após várias tentativas.")
#                 return None

# def verificar_tabelas(conn):
#     """
#     Verifica a existência das tabelas necessárias no banco de dados.

#     Args:
#     conn: Conexão com o banco de dados.
#     """
#     tabelas = ['Colheita', 'Clima', 'MaturidadeCana', 'CondicoesSolo']
#     cursor = conn.cursor()
#     for tabela in tabelas:
#         try:
#             cursor.execute(f"SELECT 1 FROM {tabela} WHERE ROWNUM = 1")
#             logging.info(f"Tabela {tabela} existe.")
#         except oracledb.DatabaseError as e:
#             if 'ORA-00942' in str(e):
#                 logging.warning(f"Tabela {tabela} não existe.")
#             else:
#                 logging.error(f"Erro ao verificar tabela {tabela}: {e}")
#     cursor.close()

# def criar_tabelas(conn):
#     """
#     Cria as tabelas necessárias no banco de dados.

#     Args:
#     conn: Conexão com o banco de dados.
#     """
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             CREATE TABLE Colheita (
#                 ano NUMBER PRIMARY KEY,
#                 quantidade_colhida NUMBER
#             )
#         """)
#         cursor.execute("""
#             CREATE TABLE Clima (
#                 ano NUMBER PRIMARY KEY,
#                 temperatura_media NUMBER,
#                 precipitacao NUMBER
#             )
#         """)
#         cursor.execute("""
#             CREATE TABLE MaturidadeCana (
#                 ano NUMBER PRIMARY KEY,
#                 indice_maturidade NUMBER
#             )
#         """)
#         cursor.execute("""
#             CREATE TABLE CondicoesSolo (
#                 ano NUMBER PRIMARY KEY,
#                 ph NUMBER,
#                 nutrientes NUMBER
#             )
#         """)
#         conn.commit()
#         logging.info("Tabelas criadas com sucesso.")
#     except oracledb.DatabaseError as e:
#         logging.error(f"Erro ao criar tabelas: {e}")
#     finally:
#         cursor.close()

# Funções de manipulação de dados
def gerar_dados_simulados():
    """
    Gera dados simulados para teste.

    Returns:
    List[DadosCompletos]: Lista de objetos DadosCompletos com dados simulados.
    """
    return [
        DadosCompletos(
            colheita=Colheita(ano=2021, quantidade_colhida=1500),
            clima=Clima(ano=2021, temperatura_media=25.3, precipitacao=1200),
            maturidade=MaturidadeCana(ano=2021, indice_maturidade=0.85),
            solo=CondicoesSolo(ano=2021, ph=6.5, nutrientes=0.75)
        ),
        DadosCompletos(
            colheita=Colheita(ano=2022, quantidade_colhida=1600),
            clima=Clima(ano=2022, temperatura_media=26.1, precipitacao=1100),
            maturidade=MaturidadeCana(ano=2022, indice_maturidade=0.88),
            solo=CondicoesSolo(ano=2022, ph=6.4, nutrientes=0.78)
        ),
        DadosCompletos(
            colheita=Colheita(ano=2023, quantidade_colhida=1550),
            clima=Clima(ano=2023, temperatura_media=25.8, precipitacao=1150),
            maturidade=MaturidadeCana(ano=2023, indice_maturidade=0.86),
            
                        solo=CondicoesSolo(ano=2023, ph=6.6, nutrientes=0.76)
        )
    ]

def carregar_dados_db(conn):
    """
    Carrega dados do banco de dados.

    Args:
    conn: Conexão com o banco de dados.

    Returns:
    pandas.DataFrame: DataFrame contendo os dados carregados do banco.
    """
    try:
        engine = create_engine(f'oracle+oracledb://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_DSN}')
        query = """
        SELECT c.ano, c.quantidade_colhida, cl.temperatura_media, cl.precipitacao, 
               m.indice_maturidade, s.ph, s.nutrientes
        FROM Colheita c
        JOIN Clima cl ON c.ano = cl.ano
        JOIN MaturidadeCana m ON c.ano = m.ano
        JOIN CondicoesSolo s ON c.ano = s.ano
        """
        df = pd.read_sql(query, engine)
        logging.info("Dados carregados do banco com sucesso")
        return df
    except Exception as e:
        logging.error(f"Erro ao carregar dados do banco: {e}")
        return None

# Funções de machine learning
def preparar_dados(df):
    """
    Prepara os dados para o modelo de machine learning.

    Args:
    df (pandas.DataFrame): DataFrame contendo os dados.

    Returns:
    tuple: Features (X) e target (y) para o modelo.
    """
    X = df[['temperatura_media', 'precipitacao', 'indice_maturidade', 'ph', 'nutrientes']]
    y = df['quantidade_colhida']
    return X, y

def treinar_modelo(X, y):
    """
    Treina o modelo de machine learning.

    Args:
    X: Features para treinamento.
    y: Target para treinamento.

    Returns:
    RandomForestRegressor: Modelo treinado.
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    previsoes = modelo.predict(X_test)
    erro = mean_squared_error(y_test, previsoes, squared=False)
    logging.info(f'Modelo treinado. Erro médio absoluto: {erro:.2f} toneladas')
    return modelo

def fazer_previsao(modelo, gerenciador):
    """
    Faz uma previsão usando o modelo treinado.

    Args:
    modelo: Modelo de machine learning treinado.
    gerenciador: Instância de GerenciadorDados.
    """
    print("\nInsira os dados para a previsão:")
    temperatura = input_float("Temperatura média: ")
    precipitacao = input_float("Precipitação: ")
    indice_maturidade = input_float("Índice de maturidade: ")
    ph = input_float("pH do solo: ")
    nutrientes = input_float("Quantidade de nutrientes: ")

    dados_previsao = pd.DataFrame([[temperatura, precipitacao, indice_maturidade, ph, nutrientes]], 
                                  columns=['temperatura_media', 'precipitacao', 'indice_maturidade', 'ph', 'nutrientes'])
    
    previsao = modelo.predict(dados_previsao)
    print(f"\nPrevisão de colheita: {previsao[0]:.2f} toneladas")
    logging.info(f"Previsão realizada: {previsao[0]:.2f} toneladas")

# Funções de visualização
def criar_graficos(gerenciador):
    """
    Cria gráficos baseados nos dados do gerenciador.

    Args:
    gerenciador: Instância de GerenciadorDados.
    """
    anos = list(gerenciador.dados_por_ano.keys())
    quantidades = [dados.colheita.quantidade_colhida for dados in gerenciador.dados_por_ano.values()]
    temperaturas = [dados.clima.temperatura_media for dados in gerenciador.dados_por_ano.values()]
    precipitacoes = [dados.clima.precipitacao for dados in gerenciador.dados_por_ano.values()]

    plt.figure(figsize=(10, 6))
    plt.plot(anos, quantidades, marker='o')
    plt.title('Quantidade Colhida ao Longo dos Anos')
    plt.xlabel('Ano')
    plt.ylabel('Quantidade Colhida')
    plt.grid(True)
    plt.savefig('quantidade_colhida.png')
    plt.close()

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    ax1.bar(anos, temperaturas, color='r', alpha=0.5, label='Temperatura Média')
    ax2.bar(anos, precipitacoes, color='b', alpha=0.5, label='Precipitação')
    ax1.set_xlabel('Ano')
    ax1.set_ylabel('Temperatura Média (°C)', color='r')
    ax2.set_ylabel('Precipitação (mm)', color='b')
    plt.title('Temperatura Média e Precipitação por Ano')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.savefig('clima.png')
    plt.close()

    logging.info("Gráficos criados e salvos como 'quantidade_colhida.png' e 'clima.png'")
    print("Gráficos criados e salvos como 'quantidade_colhida.png' e 'clima.png'")

# Funções auxiliares
def input_float(prompt):
    """
    Solicita entrada do usuário e converte para float.

    Args:
    prompt (str): Mensagem a ser exibida ao usuário.

    Returns:
    float: Valor inserido pelo usuário.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Por favor, insira um número válido.")

def validar_ano(ano):
    """
    Valida o ano inserido.

    Args:
    ano (int): Ano a ser validado.

    Returns:
    int: Ano validado.

    Raises:
    ValueError: Se o ano for inválido.
    """
    atual = datetime.now().year
    if ano < 1900 or ano > atual + 1:
        raise ValueError(f"Ano deve estar entre 1900 e {atual + 1}")
    return ano

# Funções de persistência
def salvar_estado(gerenciador, arquivo='estado.pkl'):
    """
    Salva o estado atual do gerenciador em um arquivo.

    Args:
    gerenciador: Instância de GerenciadorDados.
    arquivo (str): Nome do arquivo para salvar o estado.
    """
    with open(arquivo, 'wb') as f:
        pickle.dump(gerenciador, f)
    logging.info(f"Estado do gerenciador salvo em {arquivo}")

def carregar_estado(arquivo='estado.pkl'):
    """
    Carrega o estado do gerenciador de um arquivo.

    Args:
    arquivo (str): Nome do arquivo para carregar o estado.

    Returns:
    GerenciadorDados: Instância carregada do gerenciador.
    """
    try:
        with open(arquivo, 'rb') as f:
            gerenciador = pickle.load(f)
        logging.info(f"Estado do gerenciador carregado de {arquivo}")
        return gerenciador
    except FileNotFoundError:
        logging.warning(f"Arquivo {arquivo} não encontrado. Criando novo gerenciador.")
        return GerenciadorDados()
    
#Função do menu principal
def menu_principal():
    """
    Função principal que exibe o menu e gerencia as interações do usuário.
    """ 
    conn = None
    try:
        conn = conectar_banco()
        if not conn:
            logging.error("Não foi possível conectar ao banco de dados. Encerrando o programa.")
            return

        setup_banco_dados(conn)
        gerenciador = carregar_estado()
        modelo = None

        while True:
            print("\n=== Menu Principal ===")
            print("1. Inserir dados simulados")
            print("2. Alterar dados")
            print("3. Incluir novos dados")
            print("4. Excluir um dado específico")
            print("5. Excluir todos os dados")
            print("6. Carregar dados de arquivo JSON")
            print("7. Carregar dados do banco")
            print("8. Treinar modelo de previsão")
            print("9. Fazer previsão de colheita")
            print("10. Agendar colheita")
            print("11. Listar agendamentos de colheita")
            print("12. Alocar recursos")
            print("13. Listar recursos alocados")
            print("14. Criar gráficos")
            print("15. Sincronizar com banco de dados")
            print("16. Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                dados_simulados = gerar_dados_simulados()
                for dados in dados_simulados:
                    gerenciador.adicionar_dados(dados)
                print("Dados simulados inseridos com sucesso.")
            elif opcao == '2':
                ano = validar_ano(int(input("Digite o ano dos dados que deseja alterar: ")))
                campo = input("Digite o campo que deseja alterar (quantidade_colhida, temperatura_media, precipitacao, indice_maturidade, ph, nutrientes): ")
                valor = input_float("Digite o novo valor: ")
                gerenciador.alterar_dados(ano, campo, valor)
                print("Dados alterados com sucesso.")
            elif opcao == '3':
                ano = validar_ano(int(input("Ano: ")))
                quantidade_colhida = input_float("Quantidade colhida: ")
                temperatura_media = input_float("Temperatura média: ")
                precipitacao = input_float("Precipitação: ")
                indice_maturidade = input_float("Índice de maturidade: ")
                ph = input_float("pH do solo: ")
                nutrientes = input_float("Quantidade de nutrientes: ")
                
                novos_dados = DadosCompletos(
                    colheita=Colheita(ano=ano, quantidade_colhida=quantidade_colhida),
                    clima=Clima(ano=ano, temperatura_media=temperatura_media, precipitacao=precipitacao),
                    maturidade=MaturidadeCana(ano=ano, indice_maturidade=indice_maturidade),
                    solo=CondicoesSolo(ano=ano, ph=ph, nutrientes=nutrientes)
                )
                gerenciador.adicionar_dados(novos_dados)
                print("Novos dados incluídos com sucesso.")
            elif opcao == '4':
                ano = validar_ano(int(input("Digite o ano dos dados que deseja excluir: ")))
                gerenciador.excluir_dados(ano)
                print("Dados excluídos com sucesso.")
            elif opcao == '5':
                confirmacao = input("ATENÇÃO: Isso irá excluir TODOS os dados. Digite 'CONFIRMAR' para prosseguir: ")
                if confirmacao == 'CONFIRMAR':
                    gerenciador.excluir_todos_dados()
                    print("Todos os dados foram excluídos.")
                else:
                    print("Operação cancelada.")
            elif opcao == '6':
                arquivo = input("Digite o nome do arquivo JSON: ")
                gerenciador.carregar_dados_json(arquivo)
            elif opcao == '7':
                df = carregar_dados_db(conn)
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        dados = DadosCompletos(
                            colheita=Colheita(ano=row['ano'], quantidade_colhida=row['quantidade_colhida']),
                            clima=Clima(ano=row['ano'], temperatura_media=row['temperatura_media'], precipitacao=row['precipitacao']),
                            maturidade=MaturidadeCana(ano=row['ano'], indice_maturidade=row['indice_maturidade']),
                            solo=CondicoesSolo(ano=row['ano'], ph=row['ph'], nutrientes=row['nutrientes'])
                        )
                        gerenciador.adicionar_dados(dados)
                    print("Dados carregados do banco com sucesso.")
                else:
                    print("Não foi possível carregar dados do banco.")
            elif opcao == '8':
                df = pd.DataFrame([asdict(dados) for dados in gerenciador.dados_por_ano.values()])
                if not df.empty:
                    X, y = preparar_dados(df)
                    modelo = treinar_modelo(X, y)
                    print("Modelo treinado com sucesso!")
                else:
                    print("Não há dados suficientes para treinar o modelo.")
            elif opcao == '9':
                if modelo is None:
                    print("Primeiro treine o modelo usando a opção 8.")
                else:
                    fazer_previsao(modelo, gerenciador)
            elif opcao == '10':
                plantacao_id = int(input("ID da plantação: "))
                data_colheita = datetime.strptime(input("Data da colheita (YYYY-MM-DD): "), "%Y-%m-%d")
                gerenciador.agendar_colheita(plantacao_id, data_colheita)
                print("Colheita agendada com sucesso.")
            elif opcao == '11':
                agendamentos = gerenciador.listar_agendamentos()
                if agendamentos:
                    print("\nAgendamentos de Colheita:")
                    for data, plantacao_id in agendamentos:
                        print(f"Plantação ID: {plantacao_id}, Data Colheita: {data.strftime('%Y-%m-%d')}")
                else:
                    print("Não há agendamentos de colheita.")
            elif opcao == '12':
                recurso = input("Digite o tipo de recurso a ser alocado: ")
                gerenciador.alocar_recurso(recurso)
                print("Recurso alocado com sucesso.")
            elif opcao == '13':
                recursos = gerenciador.recursos_alocados
                if recursos:
                    print("\nRecursos Alocados:")
                    for recurso in recursos:
                        print(recurso)
                else:
                    print("Não há recursos alocados.")
            elif opcao == '14':
                criar_graficos(gerenciador)
            elif opcao == '15':
                gerenciador.sincronizar_com_banco(conn)
                print("Dados sincronizados com o banco de dados.")
            elif opcao == '16':
                salvar_estado(gerenciador)
                print("Saindo do programa...")
                break
            else:
                print("Opção inválida. Por favor, tente novamente.")

    except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            print(f"Ocorreu um erro: {e}")

    finally:
            if conn:
                fechar_conexao(conn)
            logging.info("Conexão com o banco de dados fechada")


# Testes unitários
class TestGerenciadorDados(unittest.TestCase):
    def setUp(self):
        self.gerenciador = GerenciadorDados()

    def test_adicionar_dados(self):
        dados = DadosCompletos(
            colheita=Colheita(ano=2024, quantidade_colhida=1700),
            clima=Clima(ano=2024, temperatura_media=26.0, precipitacao=1180),
            maturidade=MaturidadeCana(ano=2024, indice_maturidade=0.87),
            solo=CondicoesSolo(ano=2024, ph=6.5, nutrientes=0.77)
        )
        self.gerenciador.adicionar_dados(dados)
        self.assertIn(2024, self.gerenciador.dados_por_ano)
        self.assertEqual(self.gerenciador.dados_por_ano[2024], dados)

    def test_alterar_dados(self):
        dados = DadosCompletos(
            colheita=Colheita(ano=2024, quantidade_colhida=1700),
            clima=Clima(ano=2024, temperatura_media=26.0, precipitacao=1180),
            maturidade=MaturidadeCana(ano=2024, indice_maturidade=0.87),
            solo=CondicoesSolo(ano=2024, ph=6.5, nutrientes=0.77)
        )
        self.gerenciador.adicionar_dados(dados)
        self.gerenciador.alterar_dados(2024, 'quantidade_colhida', 1800)
        self.assertEqual(self.gerenciador.dados_por_ano[2024].colheita.quantidade_colhida, 1800)

    def test_excluir_dados(self):
        dados = DadosCompletos(
            colheita=Colheita(ano=2024, quantidade_colhida=1700),
            clima=Clima(ano=2024, temperatura_media=26.0, precipitacao=1180),
            maturidade=MaturidadeCana(ano=2024, indice_maturidade=0.87),
            solo=CondicoesSolo(ano=2024, ph=6.5, nutrientes=0.77)
        )
        self.gerenciador.adicionar_dados(dados)
        self.gerenciador.excluir_dados(2024)
        self.assertNotIn(2024, self.gerenciador.dados_por_ano)

    def test_agendar_colheita(self):
        self.gerenciador.agendar_colheita(1, datetime(2024, 5, 1))
        agendamentos = self.gerenciador.listar_agendamentos()
        self.assertEqual(len(agendamentos), 1)
        self.assertEqual(agendamentos[0][1], 1)  # plantacao_id
        self.assertEqual(agendamentos[0][0], datetime(2024, 5, 1))  # data_colheita

    def test_alocar_recurso(self):
        self.gerenciador.alocar_recurso("Trator")
        self.assertIn("Trator", self.gerenciador.recursos_alocados)

# Executar o menu principal
if __name__ == "__main__":
    menu_principal()
