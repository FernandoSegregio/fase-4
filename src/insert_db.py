# src/insert_data.py
import os
import oracledb
from dotenv import load_dotenv

from log.logger_config import configurar_logging  # Importa o logger configurado
from setup_db import criar_tabelas  # Importa a função de criação de tabelas (opcional)

# Configura o logging
logger = configurar_logging()

def gerar_dados_simulados():
    """
    Gera os dados simulados para inserção.
    """
    dados = [
        {
            "ano": 2021,
            "quantidade_colhida": 1500,
            "clima": {
                "temperatura_media": 25.3,
                "precipitacao": 1200
            },
            "maturidade_cana": {
                "indice_maturidade": 0.85
            },
            "condicoes_solo": {
                "ph": 6.5,
                "nutrientes": 0.75
            }
        },
        {
            "ano": 2022,
            "quantidade_colhida": 1600,
            "clima": {
                "temperatura_media": 26.1,
                "precipitacao": 1100
            },
            "maturidade_cana": {
                "indice_maturidade": 0.88
            },
            "condicoes_solo": {
                "ph": 6.4,
                "nutrientes": 0.78
            }
        },
        {
            "ano": 2023,
            "quantidade_colhida": 1550,
            "clima": {
                "temperatura_media": 25.8,
                "precipitacao": 1150
            },
            "maturidade_cana": {
                "indice_maturidade": 0.86
            },
            "condicoes_solo": {
                "ph": 6.6,
                "nutrientes": 0.76
            }
        }
    ]
    logger.info("Dados simulados gerados.")
    return dados

def conectar_banco(logger):
    """
    Conecta ao banco de dados Oracle utilizando as variáveis de ambiente.
    
    :param logger: Logger para registrar mensagens.
    :return: Objeto de conexão ou None em caso de erro.
    """
    load_dotenv()  # Carrega as variáveis de ambiente
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    dsn = os.getenv('DB_DSN')

    # Verificar se as variáveis de ambiente foram carregadas
    if not all([user, password, dsn]):
        logger.error("Uma ou mais variáveis de ambiente não estão definidas.")
        return None

    try:
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        logger.info("Conectado ao banco de dados.")
        return conn
    except oracledb.DatabaseError as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def verificar_dados_existentes(conn, logger):
    """
    Verifica se já existem dados na tabela 'colheita'.
    
    :param conn: Conexão com o banco de dados.
    :param logger: Logger para registrar mensagens.
    :return: True se existirem dados, False caso contrário.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM colheita")
        count = cursor.fetchone()[0]
        logger.info(f"Quantidade de registros na tabela 'colheita': {count}")
        return count > 0
    except oracledb.DatabaseError as e:
        logger.error(f"Erro ao verificar dados existentes: {e}")
        return False
    finally:
        cursor.close()

def inserir_dados(conn, dados, logger):
    """
    Insere os dados simulados nas tabelas correspondentes.
    
    :param conn: Conexão com o banco de dados Oracle.
    :param dados: Lista de dicionários com os dados a serem inseridos.
    :param logger: Logger para registrar mensagens.
    """
    cursor = conn.cursor()
    try:
        for item in dados:
            # Criar uma variável de ligação para id_colheita
            id_colheita_var = cursor.var(int)

            # Inserir na tabela colheita com RETURNING INTO
            cursor.execute("""
                INSERT INTO colheita (ano, quantidade_colhida)
                VALUES (:ano, :quantidade_colhida)
                RETURNING id_colheita INTO :id_colheita
            """, ano=item["ano"], quantidade_colhida=item["quantidade_colhida"], id_colheita=id_colheita_var)

            # Recuperar o valor de id_colheita
            id_colheita = id_colheita_var.getvalue()[0]
            logger.info(f"Registro inserido na tabela 'colheita' com id_colheita: {id_colheita}")

            # Inserir na tabela clima
            clima = item["clima"]
            cursor.execute("""
                INSERT INTO clima (id_colheita, temperatura_media, precipitacao)
                VALUES (:id_colheita, :temperatura_media, :precipitacao)
            """, id_colheita=id_colheita, temperatura_media=clima["temperatura_media"], precipitacao=clima["precipitacao"])
            logger.info(f"Registro inserido na tabela 'clima' para id_colheita: {id_colheita}")

            # Inserir na tabela maturidade_cana
            maturidade = item["maturidade_cana"]
            cursor.execute("""
                INSERT INTO maturidade_cana (id_colheita, indice_maturidade)
                VALUES (:id_colheita, :indice_maturidade)
            """, id_colheita=id_colheita, indice_maturidade=maturidade["indice_maturidade"])
            logger.info(f"Registro inserido na tabela 'maturidade_cana' para id_colheita: {id_colheita}")

            # Inserir na tabela condicoes_solo
            solo = item["condicoes_solo"]
            cursor.execute("""
                INSERT INTO condicoes_solo (id_colheita, ph, nutrientes)
                VALUES (:id_colheita, :ph, :nutrientes)
            """, id_colheita=id_colheita, ph=solo["ph"], nutrientes=solo["nutrientes"])
            logger.info(f"Registro inserido na tabela 'condicoes_solo' para id_colheita: {id_colheita}")

        # Commit das inserções
        conn.commit()
        logger.info("Dados inseridos com sucesso.")
    except oracledb.DatabaseError as e:
        logger.error(f"Erro ao inserir dados: {e}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    # Conecta ao banco de dados
    conn = conectar_banco(logger)
    if conn:
        # Opcional: Cria as tabelas se ainda não existirem
        criar_tabelas(conn, logger)

        # Verifica se já existem dados na tabela 'colheita' para evitar duplicações
        if not verificar_dados_existentes(conn, logger):
            dados = gerar_dados_simulados()
            inserir_dados(conn, dados, logger)
        else:
            logger.info("Dados já existem no banco de dados. Inserção não realizada.")

        # Fecha a conexão
        conn.close()
        logger.info("Conexão com o banco de dados encerrada.")

if __name__ == "__main__":
    main()
