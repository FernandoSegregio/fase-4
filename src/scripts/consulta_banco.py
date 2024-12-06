import os
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st

class Config:
    user = os.getenv('DB_USER') or st.secrets["database"]["user"]
    password = os.getenv('DB_PASSWORD') or st.secrets["database"]["password"] 
    dsn = os.getenv('DB_DSN') or st.secrets["database"]["dsn"]

def carregar_dados_umidade(conn, logging):
    """
    Carrega dados de leitura e umidade do banco de dados, formata a hora e exibe em formato de tabela.
    Adiciona uma coluna indicando o estado da bomba com base na umidade.

    Args:
    conn: Conexão com o banco de dados.
    logging: Instância de logging para registrar atividades.

    Returns:
    pandas.DataFrame: DataFrame contendo os dados de leitura e umidade com o estado da bomba.
    """
    try:
        # Conexão usando SQLAlchemy com o Oracle
        engine = create_engine(f'oracle+oracledb://{Config.user}:{Config.password}@{Config.dsn}')
        
        # Query para carregar apenas dados de leitura e umidade
        query = """
        SELECT 
            data_leitura, hora_leitura, valor_umidade_leitura
        FROM 
            LEITURA_SENSOR_UMIDADE
        ORDER BY 
            data_leitura ASC
        """
        
        # Executa a query e carrega os dados em um DataFrame
        df = pd.read_sql(query, engine)
        logging.info("Dados de umidade carregados do banco com sucesso.")
        
        # Formatando a coluna 'hora_leitura' para exibir apenas horas, minutos e segundos
        df['hora_leitura'] = pd.to_datetime(df['hora_leitura']).dt.strftime('%H:%M:%S')
        
        # Adicionar coluna com o estado da bomba
        df['estado_bomba'] = df['valor_umidade_leitura'].apply(lambda x: "bomba ligada" if x < 50 else "bomba desligada")
        
        # Configurações de exibição para mostrar todas as colunas no terminal
        pd.set_option('display.max_columns', None)  # Mostra todas as colunas
        pd.set_option('display.width', 1000)        # Ajusta a largura para o terminal
        pd.set_option('display.max_rows', None)     # Mostra todas as linhas (ou limite conforme necessário)

        # Exibe a tabela no terminal
        print("\n=== Dados de Leitura e Umidade ===")
        
        return df

    except Exception as e:
        logging.error(f"Erro ao carregar dados de umidade do banco: {e}")
        print("Erro ao carregar dados de umidade do banco.")
        return None
