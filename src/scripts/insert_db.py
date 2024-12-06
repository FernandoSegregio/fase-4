# src/insert_data.py
import os
import oracledb
from dotenv import load_dotenv
from dados_simulados import gerar_dados_simulados
import streamlit as st

from log.logger_config import configurar_logging
from scripts.setup_db import setup_banco_dados

# Configura o logging
logger = configurar_logging()

def conectar_banco():
    """
    Conecta ao banco de dados Oracle utilizando as variáveis de ambiente.
    
    :return: Objeto de conexão ou None em caso de erro.
    """
    load_dotenv()
    user = os.getenv('DB_USER') or st.secrets["database"]["user"]
    password = os.getenv('DB_PASSWORD') or st.secrets["database"]["password"] 
    dsn = os.getenv('DB_DSN') or st.secrets["database"]["dsn"]

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

def verificar_dados_existentes(conn):
    """
    Verifica se já existem dados na tabela 'Colheita'.
    
    :param conn: Conexão com o banco de dados.
    :return: True se existirem dados, False caso contrário.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM Colheita")
        count = cursor.fetchone()[0]
        logger.info(f"Quantidade de registros na tabela 'Colheita': {count}")
        return count > 0
    except oracledb.DatabaseError as e:
        logger.error(f"Erro ao verificar dados existentes: {e}")
        return False
    finally:
        cursor.close()

def inserir_dados(conn, dados):
    """
    Insere os dados simulados nas tabelas correspondentes.
    
    :param conn: Conexão com o banco de dados Oracle.
    :param dados: Lista de objetos DadosCompletos com os dados a serem inseridos.
    """
    cursor = conn.cursor()
    try:
        for item in dados:
            # Inserir na tabela Colheita
            cursor.execute("""
                INSERT INTO Colheita (ano, quantidade_colhida)
                VALUES (:ano, :quantidade_colhida)
            """, ano=item.colheita.ano, quantidade_colhida=item.colheita.quantidade_colhida)
            logger.info(f"Registro inserido na tabela 'Colheita' para o ano: {item.colheita.ano}")

            # Inserir na tabela Clima
            cursor.execute("""
                INSERT INTO Clima (ano, temperatura_media, precipitacao)
                VALUES (:ano, :temperatura_media, :precipitacao)
            """, ano=item.clima.ano, temperatura_media=item.clima.temperatura_media, precipitacao=item.clima.precipitacao)
            logger.info(f"Registro inserido na tabela 'Clima' para o ano: {item.clima.ano}")

            # Inserir na tabela MaturidadeCana
            cursor.execute("""
                INSERT INTO MaturidadeCana (ano, indice_maturidade)
                VALUES (:ano, :indice_maturidade)
            """, ano=item.maturidade.ano, indice_maturidade=item.maturidade.indice_maturidade)
            logger.info(f"Registro inserido na tabela 'MaturidadeCana' para o ano: {item.maturidade.ano}")

            # Inserir na tabela CondicoesSolo
            cursor.execute("""
                INSERT INTO CondicoesSolo (ano, ph, nutrientes)
                VALUES (:ano, :ph, :nutrientes)
            """, ano=item.solo.ano, ph=item.solo.ph, nutrientes=item.solo.nutrientes)
            logger.info(f"Registro inserido na tabela 'CondicoesSolo' para o ano: {item.solo.ano}")

            

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
    conn = conectar_banco()
    if conn:
        # Configura o banco de dados
        setup_banco_dados(conn)

        # Verifica se já existem dados na tabela 'Colheita' para evitar duplicações
        if not verificar_dados_existentes(conn):
            dados = gerar_dados_simulados()
            inserir_dados(conn, dados)
        else:
            logger.info("Dados já existem no banco de dados. Inserção não realizada.")

        # Fecha a conexão
        conn.close()
        logger.info("Conexão com o banco de dados encerrada.")

if __name__ == "__main__":
    main()