import os
import json
import oracledb
import logging
from dotenv import load_dotenv
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict
from queue import PriorityQueue

# Carregamento de variáveis de ambiente
load_dotenv()

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
class GerenciadorDados():
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

    def alocar_recurso(self, conn):
        try:
            cursor = conn.cursor()

            # Recuperar IDs da colheita
            cursor.execute("SELECT ano FROM Colheita")
            colheita_ids = cursor.fetchall()

            # Exibir IDs de colheita disponíveis
            if colheita_ids:
                print("\nIDs de colheita disponíveis:")
                for i, (ano,) in enumerate(colheita_ids, 1):
                    print(f"{i}. {ano}")
            else:
                print("Não há colheitas registradas.")
                return

            # Solicitar ao usuário que escolha um ID de colheita
            escolha_id = int(input("\nEscolha o ID da plantação pelo número: ")) - 1
            if 0 <= escolha_id < len(colheita_ids):
                colheita_id = colheita_ids[escolha_id][0]
            else:
                print("Escolha inválida.")
                return

            # Lista de tipos de recursos disponíveis
            tipos_recursos = ["colhedora", "trator", "pulverizador", "irrigador", "mão de obra"]

            # Exibindo as opções de recursos para o usuário
            print("\nTipos de recursos disponíveis:")
            for i, recurso in enumerate(tipos_recursos, 1):
                print(f"{i}. {recurso}")
            
            # Solicitando ao usuário que escolha um recurso
            escolha = int(input("\nEscolha o tipo de recurso pelo número: ")) - 1
            if 0 <= escolha < len(tipos_recursos):
                tipo_recurso = tipos_recursos[escolha]
            else:
                print("Escolha inválida.")
                return

            quantidade = int(input("Quantidade: "))
            
            # Inserindo os dados no banco de dados
            sql = "INSERT INTO recursos_alocados (colheita_id, tipo_recurso, quantidade) VALUES (:1, :2, :3)"
            cursor.execute(sql, (colheita_id, tipo_recurso, quantidade))
            conn.commit()
            print("Recursos alocados com sucesso.")
            
        except ValueError:
            print("Erro: Por favor, insira um número válido.")
        except oracledb.DatabaseError as e:
            print(f"Erro ao alocar recursos: {e}")
        finally:
            cursor.close()


    def listar_arquivos_json(self, pasta):
        arquivos_json = [arquivo for arquivo in os.listdir(pasta) if arquivo.lower().endswith('.json')]
        return arquivos_json

    def carregar_dados_json(self, pasta='src/dados_banco'):
        """
        Carrega dados de um arquivo JSON escolhido pelo usuário.

        Args:
        pasta (str): Pasta onde os arquivos JSON estão localizados.
        """
        arquivos_json = self.listar_arquivos_json(pasta)

        if not arquivos_json:
            print("Não há arquivos JSON na pasta.")
            return

        print("\nDados de colheitas nos arquivos JSON disponíveis (de acordo com o ano da colheita):")
        for i, arquivo in enumerate(arquivos_json, 1):
            print(f"{i}. {arquivo}")

        escolha = self.escolher_arquivo(arquivos_json)

        if escolha is not None:
            nome_arquivo = arquivos_json[escolha]
            caminho_arquivo = os.path.join(pasta, nome_arquivo)
            
            try:
                with open(caminho_arquivo, 'r') as arquivo:
                    dados_json = json.load(arquivo)
                self.processar_dados_json(dados_json)
                print(f"Dados do arquivo {nome_arquivo} carregados com sucesso.")
            except json.JSONDecodeError:
                print(f"Erro: O arquivo {nome_arquivo} não é um JSON válido.")
            except Exception as e:
                print(f"Erro ao carregar dados do arquivo JSON: {e}")

    def escolher_arquivo(self, arquivos_json):
        try:
            escolha = int(input("\nEscolha o número do arquivo que deseja carregar: ")) - 1
            if 0 <= escolha < len(arquivos_json):
                return escolha
            else:
                print("Escolha inválida.")
                return None
        except ValueError:
            print("Por favor, insira um número válido.")
            return None
        
    def processar_dados_json(self, dados_json):
        for dado in dados_json:
            dados_completos = DadosCompletos(
                colheita=Colheita(ano=dado['ano'], quantidade_colhida=dado['quantidade_colhida']),
                clima=Clima(ano=dado['ano'], temperatura_media=dado['clima']['temperatura_media'], precipitacao=dado['clima']['precipitacao']),
                maturidade=MaturidadeCana(ano=dado['ano'], indice_maturidade=dado['maturidade_cana']['indice_maturidade']),
                solo=CondicoesSolo(ano=dado['ano'], ph=dado['condicoes_solo']['ph'], nutrientes=dado['condicoes_solo']['nutrientes'])
            )
            self.adicionar_dados(dados_completos)

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
                        try:
                            cursor.execute("""
                                INSERT INTO Colheita (ano, quantidade_colhida)
                                VALUES (:ano, :quantidade_colhida)
                            """, ano=dados['colheita']['ano'], quantidade_colhida=dados['colheita']['quantidade_colhida'])
                            logging.info(f"Registro inserido na tabela 'Colheita' para o ano: {dados['colheita']['ano']}")
                            
                            cursor.execute("""
                                INSERT INTO Clima (ano, temperatura_media, precipitacao)
                                VALUES (:ano, :temperatura_media, :precipitacao)
                            """, ano=dados['clima']['ano'], temperatura_media=dados['clima']['temperatura_media'], precipitacao=dados['clima']['precipitacao'])
                            logging.info(f"Registro inserido na tabela 'Clima' para o ano: {dados['clima']['ano']}")
                            
                            cursor.execute("""
                                INSERT INTO MaturidadeCana (ano, indice_maturidade)
                                VALUES (:ano, :indice_maturidade)
                            """, ano=dados['maturidade']['ano'], indice_maturidade=dados['maturidade']['indice_maturidade'])
                            logging.info(f"Registro inserido na tabela 'MaturidadeCana' para o ano: {dados['maturidade']['ano']}")
                            
                            cursor.execute("""
                                INSERT INTO CondicoesSolo (ano, ph, nutrientes)
                                VALUES (:ano, :ph, :nutrientes)
                            """, ano=dados['solo']['ano'], ph=dados['solo']['ph'], nutrientes=dados['solo']['nutrientes'])
                            logging.info(f"Registro inserido na tabela 'CondicoesSolo' para o ano: {dados['solo']['ano']}")
                        except oracledb.DatabaseError as e:
                            logging.error(f"Erro ao inserir dados para o ano {dados['colheita']['ano']}: {e}")
                            raise  # Re-raise para capturar no bloco externo
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
                        
                        try:
                            cursor.execute(f"""
                                UPDATE {tabela} SET {operacao['campo']} = :valor WHERE ano = :ano
                            """, valor=operacao['valor'], ano=operacao['ano'])
                            logging.info(f"Registro atualizado na tabela '{tabela}' para o ano: {operacao['ano']}, campo: {operacao['campo']}")
                        except oracledb.DatabaseError as e:
                            logging.error(f"Erro ao atualizar dados na tabela {tabela} para o ano {operacao['ano']}: {e}")
                            raise
                    elif operacao["tipo"] == "excluir":
                        for tabela in ["Colheita", "Clima", "MaturidadeCana", "CondicoesSolo"]:
                            try:
                                cursor.execute(f"DELETE FROM {tabela} WHERE ano = :ano", ano=operacao['ano'])
                                logging.info(f"Registro excluído da tabela '{tabela}' para o ano: {operacao['ano']}")
                            except oracledb.DatabaseError as e:
                                logging.error(f"Erro ao excluir dados da tabela {tabela} para o ano {operacao['ano']}: {e}")
                                raise
                    elif operacao["tipo"] == "excluir_todos":
                        for tabela in ["Colheita", "Clima", "MaturidadeCana", "CondicoesSolo"]:
                            try:
                                cursor.execute(f"DELETE FROM {tabela}")
                                logging.info(f"Todos os registros excluídos da tabela '{tabela}'")
                            except oracledb.DatabaseError as e:
                                logging.error(f"Erro ao excluir todos os dados da tabela {tabela}: {e}")
                                raise
                
                conn.commit()
                self.operacoes_pendentes.clear()
                logging.info("Dados sincronizados com o banco de dados com sucesso")
            except Exception as e:
                conn.rollback()
                logging.error(f"Erro ao sincronizar dados com o banco: {e}")
            finally:
                cursor.close()    
    def listar_operacoes_pendentes(self):
        for operacao in self.operacoes_pendentes:
            print(operacao)