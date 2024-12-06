import os
import paho.mqtt.client as mqtt
import ssl
import oracledb
import json
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st

# Configurações do HiveMQ Cloud
mqtt_server = "91c5f1ea0f494ccebe45208ea8ffceff.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_user = "FARM_TECH"
mqtt_password = "Pato1234"

# Tópicos MQTT
humidity_topic = "sensor/umidade"
pump_topic = "sensor/bomba"
ph_sensor = "sensor/ph"
k_button_topic = "sensor/potassio"
p_button_topic = "sensor/sodio"

# Carrega as variáveis de ambiente para o banco de dados
load_dotenv()
db_user = os.getenv('DB_USER') or st.secrets["database"]["user"]
db_password = os.getenv('DB_PASSWORD') or st.secrets["database"]["password"] 
db_dsn = os.getenv('DB_DSN') or st.secrets["database"]["dsn"]

# Função para conectar ao banco de dados Oracle
def conectar_banco():
    try:
        conn = oracledb.connect(user=db_user, password=db_password, dsn=db_dsn)
        print("Conectado ao banco de dados Oracle.")
        return conn
    except oracledb.DatabaseError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para garantir que o sensor existe na tabela
def verificar_ou_inserir_sensor_umidade(conn, id_sensor):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sensor_umidade WHERE id_sensor_umidade = :id_sensor", {'id_sensor': id_sensor})
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO sensor_umidade (id_sensor_umidade) VALUES (:id_sensor)", {'id_sensor': id_sensor})
        conn.commit()
        print(f"Sensor de umidade {id_sensor} inserido com sucesso.")
    cursor.close()

def verificar_ou_inserir_sensor_ph(conn, id_sensor):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sensor_ph WHERE id_sensor_ph = :id_sensor", {'id_sensor': id_sensor})
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO sensor_ph (id_sensor_ph) VALUES (:id_sensor)", {'id_sensor': id_sensor})
        conn.commit()
        print(f"Sensor de pH {id_sensor} inserido com sucesso.")
    cursor.close()

# Função para inserir leitura de umidade
def inserir_leitura_umidade(conn, id_sensor, data_leitura, hora_leitura, valor_umidade):
    verificar_ou_inserir_sensor_umidade(conn, id_sensor)
    cursor = conn.cursor()
    try:
        # Combine data e hora em um único objeto datetime
        data_hora_leitura = datetime.strptime(f"{data_leitura} {hora_leitura}", '%Y-%m-%d %H:%M')

        umidade_formatada = round(float(valor_umidade), 2)

        cursor.execute("""
            INSERT INTO LEITURA_SENSOR_UMIDADE 
            (id_leitura_umidade, id_sensor_umidade, data_leitura, hora_leitura, valor_umidade_leitura)
            VALUES 
            (LEITURA_SENSOR_UMIDADE_SEQ.NEXTVAL, :id_sensor, :data_leitura, :hora_leitura, :valor_umidade)
        """, {
            'id_sensor': id_sensor,
            'data_leitura': data_hora_leitura.date(),
            'hora_leitura': data_hora_leitura,
            'valor_umidade': umidade_formatada
        })
        conn.commit()
        print(f"Leitura de umidade inserida com sucesso: {umidade_formatada}%")
    except oracledb.DatabaseError as e:
        print(f"Erro ao inserir dados de umidade: {e}")
        conn.rollback()
    finally:
        cursor.close()

# Função para inserir leitura de pH
def inserir_leitura_ph(conn, id_sensor, data_leitura, hora_leitura, ph_equivalente):
    verificar_ou_inserir_sensor_ph(conn, id_sensor)
    cursor = conn.cursor()
    try:
        # Combine data e hora em um único objeto datetime
        data_hora_leitura = datetime.strptime(f"{data_leitura} {hora_leitura}", '%Y-%m-%d %H:%M')

        ph_formatado = round(float(ph_equivalente), 2)

        cursor.execute("""
            INSERT INTO LEITURA_SENSOR_PH 
            (id_leitura_ph, id_sensor_ph, data_leitura, hora_leitura, valor_ph_leitura)
            VALUES 
            (LEITURA_SENSOR_PH_SEQ.NEXTVAL, :id_sensor, :data_leitura, :hora_leitura, :valor_ph)
        """, {
            'id_sensor': id_sensor,
            'data_leitura': data_hora_leitura.date(),
            'hora_leitura': data_hora_leitura,
            'valor_ph': ph_formatado
        })
        conn.commit()
        print(f"Leitura de pH inserida com sucesso: {ph_formatado}")
    except oracledb.DatabaseError as e:
        print(f"Erro ao inserir dados de pH: {e}")
        conn.rollback()
    finally:
        cursor.close()



# Função para inserir leitura de temperatura
def inserir_leitura_temperatura(conn, id_sensor, data_leitura, hora_leitura, temperatura):
    verificar_ou_inserir_sensor_umidade(conn, id_sensor)  # Verifica ou insere o sensor
    cursor = conn.cursor()
    try:
        data_leitura_formatada = datetime.strptime(data_leitura, '%Y-%m-%d').date()
        hora_leitura_formatada = datetime.strptime(hora_leitura, '%H:%M:%S')
        temperatura_formatada = round(float(temperatura), 2)

        cursor.execute("""
            INSERT INTO leitura_sensor_temperatura 
            (id_sensor_umidade, data_leitura, hora_leitura, valor_temperatura, limite_minimo_temperatura, limite_maximo_temperatura)
            VALUES (:id_sensor, :data_leitura, :hora_leitura, :valor_temperatura, :limite_minimo, :limite_maximo)
        """, {
            'id_sensor': id_sensor,
            'data_leitura': data_leitura_formatada,
            'hora_leitura': hora_leitura_formatada,
            'valor_temperatura': temperatura_formatada,
            'limite_minimo': 12.00,
            'limite_maximo': 36.00
        })
        conn.commit()
        print("Leitura de temperatura inserida com sucesso.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao inserir dados de temperatura: {e}")
        conn.rollback()
    finally:
        cursor.close()

# Função para inserir leitura do sensor de pH
# Callback para conexão
def on_connect(client, userdata, flags, rc):
    print(f"Conectado com código de resultado {rc}")
    client.subscribe(humidity_topic)
    client.subscribe(ph_sensor)
    client.subscribe(k_button_topic)
    client.subscribe(p_button_topic)

# Callback para mensagens recebidas
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Mensagem recebida: {msg.topic} - {payload}")
        
        conn = conectar_banco()
        if conn:
            if msg.topic == humidity_topic:
                # Mapear campos recebidos para os esperados
                id_sensor = payload.get("id_sensor")
                data_leitura = payload.get("DATA_LEITURA") or payload.get("data_leitura")
                hora_leitura = payload.get("HORA_LEITURA") or payload.get("hora_leitura")
                umidade = payload.get("Valor")

                if id_sensor and data_leitura and hora_leitura and umidade:
                    inserir_leitura_umidade(conn, id_sensor, data_leitura, hora_leitura, umidade)

                    # Lógica para controle da bomba
                    if float(umidade) > 50:
                        client.publish(pump_topic, "OFF")
                        print("Umidade alta, enviando 'OFF' para o tópico da bomba.")
                    else:
                        client.publish(pump_topic, "ON")
                        print("Umidade baixa, enviando 'ON' para o tópico da bomba.")
                else:
                    print("Campos faltando no payload de umidade.")

            elif msg.topic == ph_sensor:
                # Mapear campos recebidos para os esperados
                id_sensor = payload.get("id_sensor")
                data_leitura = payload.get("DATA_LEITURA") or payload.get("data_leitura")
                hora_leitura = payload.get("HORA_LEITURA") or payload.get("hora_leitura")
                ph_equivalente = payload.get("Valor")

                if id_sensor and data_leitura and hora_leitura and ph_equivalente:
                    inserir_leitura_ph(conn, id_sensor, data_leitura, hora_leitura, ph_equivalente)
                else:
                    print("Campos faltando no payload de pH.")

            conn.close()
            print("Conexão com o banco de dados encerrada.")
            
    except Exception as e:
        print(f"Erro ao processar mensagem MQTT: {e}")


# Configuração do cliente MQTT
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.on_connect = on_connect
client.on_message = on_message

# Configuração de TLS/SSL
client.tls_set(cert_reqs=ssl.CERT_NONE)

# Conexão com o broker
client.connect(mqtt_server, mqtt_port, 60)

# Inicia o loop de processamento
client.loop_forever()
