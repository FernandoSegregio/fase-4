import os
import oracledb

from dotenv import load_dotenv

load_dotenv()

# Agora você pode acessar as variáveis de ambiente como usual
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
dsn = os.getenv('DB_DSN')

# Função para conectar ao banco de dados Oracle

def conectar_banco():
    try:
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        print("Conectou") 
        return conn
    
    except oracledb.DatabaseError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

conectar_banco()

# Função para inserir dados no banco de dados
def inserir_dados_banco(conn, dados):
    try:
        cursor = conn.cursor()
        for dado in dados:
            cursor.execute("""
                INSERT INTO Colheita (ano, quantidade_colhida) VALUES (:ano, :quantidade_colhida)""",
                ano=dado['ano'], quantidade_colhida=dado['quantidade_colhida']
            )
            cursor.execute("""
                INSERT INTO Clima (ano, temperatura_media, precipitacao) VALUES (:ano, :temperatura_media, :precipitacao)""",
                ano=dado['ano'], temperatura_media=dado['clima']['temperatura_media'], precipitacao=dado['clima']['precipitacao']
            )
            cursor.execute("""
                INSERT INTO MaturidadeCana (ano, indice_maturidade) VALUES (:ano, :indice_maturidade)""",
                ano=dado['ano'], indice_maturidade=dado['maturidade_cana']['indice_maturidade']
            )
            cursor.execute("""
                INSERT INTO CondicoesSolo (ano, ph, nutrientes) VALUES (:ano, :ph, :nutrientes)""",
                ano=dado['ano'], ph=dado['condicoes_solo']['ph'], nutrientes=dado['condicoes_solo']['nutrientes']
            )
        conn.commit()
        cursor.close()
    except oracledb.DatabaseError as e:
        print(f"Erro ao inserir dados no banco de dados: {e}")

inserir_dados_banco(conectar_banco(), 'chamar função dados simulados')