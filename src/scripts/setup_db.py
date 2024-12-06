import os
from dotenv import load_dotenv
import oracledb
import logging
import streamlit as st

# Configuração do logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('setup_bd.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

def criar_sequencias_e_triggers(conn):
    """Cria sequências e triggers para IDs automáticos nas tabelas que precisam de IDs gerados automaticamente."""
    cursor = conn.cursor()
    tabelas_com_trigger = {
        'PROPRIEDADE': 'id_propriedade',
        'CAMPO': 'id_campo',
        'SENSOR_UMIDADE': 'id_sensor_umidade',
        'LEITURA_SENSOR_UMIDADE': 'id_leitura_umidade',
        'LEITURA_SENSOR_TEMPERATURA': 'id_leitura_temperatura',  # Tabela de temperatura
        'SENSOR_PH': 'id_sensor_ph',
        'LEITURA_SENSOR_PH': 'id_leitura_ph',
        'SENSOR_NUTRIENTES': 'id_sensor_nutrientes',
        'LEITURA_SENSOR_NUTRIENTES': 'id_leitura_nutrientes',
        'CLIMA': 'id_clima'
    }
    
    for tabela, id_coluna in tabelas_com_trigger.items():
        try:
            cursor.execute(f"""
                BEGIN
                    EXECUTE IMMEDIATE 'CREATE SEQUENCE {tabela}_SEQ START WITH 1 INCREMENT BY 1';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE != -955 THEN RAISE; END IF;
                END;
            """)
            logger.info(f"Sequência '{tabela}_SEQ' criada ou já existia.")
            
            cursor.execute(f"""
                CREATE OR REPLACE TRIGGER {tabela}_BI
                BEFORE INSERT ON {tabela}
                FOR EACH ROW
                WHEN (NEW.{id_coluna} IS NULL)
                BEGIN
                    SELECT {tabela}_SEQ.NEXTVAL INTO :NEW.{id_coluna} FROM dual;
                END;
            """)
            logger.info(f"Trigger '{tabela}_BI' criada para tabela '{tabela}'.")
        except oracledb.DatabaseError as e:
            logger.error(f"Erro ao criar sequência ou trigger para a tabela {tabela}: {e}")
            conn.rollback()
    cursor.close()

def tabela_existe(cursor, nome_tabela):
    cursor.execute("SELECT COUNT(*) FROM user_tables WHERE table_name = :nome_tabela", nome_tabela=nome_tabela.upper())
    return cursor.fetchone()[0] > 0

def criar_tabelas(conn):
    """Cria todas as tabelas necessárias no banco de dados Oracle se elas não existirem."""
    cursor = conn.cursor()
    try:
        tabelas = {
            'PRODUTOR': """
                CREATE TABLE Produtor (
                    produtor_id NUMBER PRIMARY KEY,
                    nome VARCHAR2(100) NOT NULL,
                    email VARCHAR2(50),
                    telefone VARCHAR2(15)
                )
            """,
            'PROPRIEDADE': """
                CREATE TABLE Propriedade (
                    id_propriedade NUMBER PRIMARY KEY,
                    id_produtor NUMBER,
                    nome VARCHAR2(100) NOT NULL,
                    localizacao VARCHAR2(255),
                    FOREIGN KEY (id_produtor) REFERENCES Produtor(produtor_id)
                )
            """,
            'CAMPO': """
                CREATE TABLE Campo (
                    id_campo NUMBER PRIMARY KEY,
                    id_propriedade NUMBER,
                    tipo_cultura VARCHAR2(100),
                    data_plantio DATE,
                    data_prevista_colheita DATE,
                    area_plantada DECIMAL(10,2),
                    status_plantio VARCHAR2(200),
                    FOREIGN KEY (id_propriedade) REFERENCES Propriedade(id_propriedade)
                )
            """,
            'SENSOR_UMIDADE': """
                CREATE TABLE Sensor_Umidade (
                    id_sensor_umidade NUMBER PRIMARY KEY,
                    id_campo NUMBER,
                    localizacao DECIMAL(10,2),
                    data_instalacao DATE,
                    hora_instalacao TIMESTAMP,
                    FOREIGN KEY (id_campo) REFERENCES Campo(id_campo)
                )
            """,
            'LEITURA_SENSOR_UMIDADE': """
                CREATE TABLE Leitura_sensor_Umidade (
                    id_leitura_umidade NUMBER PRIMARY KEY,
                    id_sensor_umidade NUMBER,
                    data_leitura DATE,
                    hora_leitura TIMESTAMP,
                    valor_umidade_leitura DECIMAL(10,2),
                    limite_minimo_umidade DECIMAL(10,2),
                    limite_maximo_umidade DECIMAL(10,2),
                    FOREIGN KEY (id_sensor_umidade) REFERENCES Sensor_Umidade(id_sensor_umidade)
                )
            """,
            'LEITURA_SENSOR_TEMPERATURA': """
                CREATE TABLE Leitura_sensor_Temperatura (
                    id_leitura_temperatura NUMBER PRIMARY KEY,
                    id_sensor_umidade NUMBER,
                    data_leitura DATE,
                    hora_leitura TIMESTAMP,
                    valor_temperatura DECIMAL(10,2),
                    limite_minimo_temperatura DECIMAL(10,2),
                    limite_maximo_temperatura DECIMAL(10,2),
                    FOREIGN KEY (id_sensor_umidade) REFERENCES Sensor_Umidade(id_sensor_umidade)
                )
            """,
            'SENSOR_PH': """
                CREATE TABLE Sensor_PH (
                    id_sensor_ph NUMBER PRIMARY KEY,
                    id_campo NUMBER,
                    localizacao DECIMAL(10,2),
                    data_instalacao DATE,
                    hora_instalacao TIMESTAMP,
                    FOREIGN KEY (id_campo) REFERENCES Campo(id_campo)
                )
            """,
            'LEITURA_SENSOR_PH': """
                CREATE TABLE Leitura_sensor_PH (
                    id_leitura_ph NUMBER PRIMARY KEY,
                    id_sensor_ph NUMBER,
                    data_leitura DATE,
                    hora_leitura TIMESTAMP,
                    valor_ph_leitura DECIMAL(10,2),
                    limite_minimo_ph DECIMAL(10,2),
                    limite_maximo_ph DECIMAL(10,2),
                    FOREIGN KEY (id_sensor_ph) REFERENCES Sensor_PH(id_sensor_ph)
                )
            """,
            'SENSOR_NUTRIENTES': """
                CREATE TABLE Sensor_Nutrientes (
                    id_sensor_nutrientes NUMBER PRIMARY KEY,
                    id_campo NUMBER,
                    localizacao DECIMAL(10,2),
                    data_instalacao DATE,
                    hora_instalacao TIMESTAMP,
                    FOREIGN KEY (id_campo) REFERENCES Campo(id_campo)
                )
            """,
            'LEITURA_SENSOR_NUTRIENTES': """
                CREATE TABLE Leitura_sensor_Nutrientes (
                    id_leitura_nutrientes NUMBER PRIMARY KEY,
                    id_sensor_nutrientes NUMBER,
                    data_leitura DATE,
                    hora_leitura TIMESTAMP,
                    valor_nutrientes_leitura DECIMAL(10,2),
                    limite_minimo_nutrientes DECIMAL(10,2),
                    limite_maximo_nutrientes DECIMAL(10,2),
                    FOREIGN KEY (id_sensor_nutrientes) REFERENCES Sensor_Nutrientes(id_sensor_nutrientes)
                )
            """,
            'CLIMA': """
                CREATE TABLE Clima (
                    id_clima NUMBER PRIMARY KEY,
                    temperatura_media DECIMAL(5,2),
                    precipitacao DECIMAL(10,2)
                )
            """,
            'NUTRIENTES': """
                CREATE TABLE Nutrientes (
                    id_nutriente NUMBER PRIMARY KEY,
                    nome_nutriente VARCHAR2(50) NOT NULL
                )
            """
        }

        for nome_tabela, comando_sql in tabelas.items():
            if not tabela_existe(cursor, nome_tabela):
                cursor.execute(comando_sql)
                logger.info(f"Tabela '{nome_tabela}' criada com sucesso.")
            else:
                logger.info(f"Tabela '{nome_tabela}' já existe.")
        
        conn.commit()
        logger.info("Todas as tabelas foram criadas ou já existiam.")
    except oracledb.DatabaseError as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        conn.rollback()
    finally:
        cursor.close()

def setup_banco_dados(conn):
    logger.info("Iniciando configuração do banco de dados")
    criar_tabelas(conn)
    criar_sequencias_e_triggers(conn)
    logger.info("Configuração do banco de dados concluída")

if __name__ == "__main__":
    load_dotenv()
    
    try:
        conn = oracledb.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dsn=os.getenv('DB_DSN')
        )
        setup_banco_dados(conn)
    except oracledb.DatabaseError as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
