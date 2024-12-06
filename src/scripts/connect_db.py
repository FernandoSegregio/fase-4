import oracledb
from dotenv import load_dotenv
from log.logger_config import configurar_logging
import os
import streamlit as st

# Configura o logging
logger = configurar_logging()

def conectar_banco():
    """
    Conecta ao banco de dados Oracle utilizando as variáveis de ambiente.
    
    :return: Objeto de conexão ou None em caso de erro.
    """
    load_dotenv()  # Carrega as variáveis de ambiente
    user = os.getenv('DB_USER') or st.secrets["database"]["user"]
    password = os.getenv('DB_PASSWORD') or st.secrets["database"]["password"] 
    dsn = os.getenv('DB_DSN') or st.secrets["database"]["dsn"]

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

def fechar_conexao(conn):
    """
    Fecha a conexão com o banco de dados.

    :param conn: Objeto de conexão com o banco de dados.
    """
    if conn:
        conn.close()
        logger.info("Conexão com o banco de dados encerrada.")

def main():
    # Conecta ao banco de dados
    conn = conectar_banco()
    if conn:
        # Configura o banco de dados
       # setup_banco_dados(conn)
        fechar_conexao(conn)

if __name__ == "__main__":
    main()