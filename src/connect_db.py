import oracledb
from dotenv import load_dotenv
from log.logger_config import configurar_logging
from setup_db import criar_tabelas
import os

def conectar_banco(logger):
    #Conecta ao banco de dados Oracle utilizando as variáveis de ambiente.
    
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

def main():
    # Configura o logging
    logger = configurar_logging()

    # Conecta ao banco de dados
    conn = conectar_banco(logger)
    if conn:
        # Chama a função para criar tabelas
        criar_tabelas(conn, logger)
        conn.close()
        logger.info("Conexão com o banco de dados encerrada.")

if __name__ == "__main__":
    main()