import os
from sqlalchemy import create_engine
import pandas as pd

class Config:
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_DSN = os.getenv('DB_DSN')


def carregar_dados_db(conn, logging):
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
        ORDER BY c.ano ASC
        """
        df = pd.read_sql(query, engine)
        logging.info("Dados carregados do banco com sucesso")
        return df
    except Exception as e:
        logging.error(f"Erro ao carregar dados do banco: {e}")
        return None