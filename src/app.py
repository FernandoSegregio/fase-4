import logging
import paho.mqtt.client as mqtt
import ssl
from dotenv import load_dotenv
import requests
import paho.mqtt.client as mqtt
import ssl
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd

from scripts.connect_db import conectar_banco, fechar_conexao
from scripts.setup_db import setup_banco_dados
from scripts.consulta_banco import carregar_dados_umidade

# Configuração de MQTT e Tópicos
mqtt_server = "91c5f1ea0f494ccebe45208ea8ffceff.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_user = "admin1"
mqtt_password = "Asd123***"
humidity_topic = "sensor/umidade"
pump_topic = "sensor/bomba"



# Configurações da API do OpenWeatherMap
API_KEY = 'c60a4792ccbe5983e113c048825b78fb'
CITY = 'Juiz de Fora'
PREDICT_DAYS = 7  # Número de dias para prever


# Função para consultar previsão do tempo
def consultar_previsao_tempo(city, api_key):
    link_rain = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(link_rain)
    
    if response.status_code == 200:
        data = response.json()
        previsao = data['list']
        
        # Verifica se existe previsão de chuva nos próximos dias
        chuva_prevista = any(item.get('pop', 0) > 0 for item in previsao[:PREDICT_DAYS * 8])  # 8 previsões por dia
        if chuva_prevista:
            print("Chuva prevista nos próximos 7 dias. Desligando a bomba de água.")
            client.publish(pump_topic, "OFF")
        else:
            print("Sem previsão de chuva nos próximos 7 dias. A bomba de água permanecerá ligada.")
    else:
        print(f"Erro ao consultar a previsão do tempo. Status code: {response.status_code}")


# Configuração de logging
logging.basicConfig(
    filename='app.log', level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configurações do cliente MQTT
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Conectado com código de resultado {rc}")
    client.subscribe(humidity_topic)


client.on_connect = on_connect
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port, 60)
client.loop_start()

# Função para ligar a bomba de água manualmente
# Defina o cliente MQTT globalmente
client = mqtt.Client()

def ligar_bomba_agua():
    global client  # Acessa o cliente MQTT globalmente
    client.publish(pump_topic, "ON")
    print("Comando 'ON' enviado para ligar a bomba de água.")

# Configuração do cliente MQTT
client.username_pw_set(mqtt_user, mqtt_password)
client.on_connect = on_connect

# Configuração de TLS/SSL
client.tls_set(cert_reqs=ssl.CERT_NONE)

# Conexão com o broker
client.connect(mqtt_server, mqtt_port, 60)

# Inicia o loop de processamento
client.loop_start()  # Inicia o loop MQTT em segundo plano

# Exemplo de chamada para ligar a bomba
ligar_bomba_agua()

# Função para desligar a bomba de água manualmente
def desligar_bomba_agua():
    client.publish(pump_topic, "OFF")
    print("Comando 'OFF' enviado para desligar a bomba de água.")

# Função para exibir dados do sensor de umidade
def exibir_dados_sensor_umidade(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM LEITURA_SENSOR_UMIDADE")
        resultados = cursor.fetchall()
        if resultados:
            for linha in resultados:
                print(linha)
        else:
            print("Nenhum dado encontrado para o sensor de umidade.")
        cursor.close()
    except Exception as e:
        logging.error(f"Erro ao exibir dados do sensor de umidade: {e}")

# Função para exibir dados do sensor de temperatura
def exibir_dados_sensor_temperatura(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM LEITURA_SENSOR_TEMPERATURA")
        resultados = cursor.fetchall()
        if resultados:
            for linha in resultados:
                print(linha)
        else:
            print("Nenhum dado encontrado para o sensor de temperatura.")
        cursor.close()
    except Exception as e:
        logging.error(f"Erro ao exibir dados do sensor de temperatura: {e}")

# Função para apagar dados do sensor de temperatura
def apagar_dados_sensor_temperatura(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM LEITURA_SENSOR_TEMPERATURA")
        conn.commit()
        print("Dados do sensor de temperatura apagados com sucesso.")
        cursor.close()
    except Exception as e:
        logging.error(f"Erro ao apagar dados do sensor de temperatura: {e}")

def apagar_dados_sensor_umidade(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM LEITURA_SENSOR_UMIDADE")
        conn.commit()
        print("Dados do sensor de umidade apagados com sucesso.")
        cursor.close()
    except Exception as e:
        logging.error(f"Erro ao apagar dados do sensor de umidade: {e}")

# Função para carregar dados do banco de dados
def carregar_dados_do_banco(conn):
    try:
        df = carregar_dados_umidade(conn, logging)
        if df is not None and not df.empty:
            print("Dados carregados com sucesso:")
            print(df)
        else:
            print("Você não tem dados para carregar.")
    except Exception as e:
        logging.error(f"Erro ao carregar dados do banco: {e}")

# Função principal para exibir o menu e gerenciar as opções do usuário
def menu_principal():
    conn = None
    try:
        # Conectar ao banco de dados
        conn = conectar_banco()
        if not conn:
            logging.error("Não foi possível conectar ao banco de dados. Encerrando o programa.")
            return

        # Configuração inicial do banco de dados
        setup_banco_dados(conn)

        while True:
            print("\n=== Menu Principal ===")
            print("1. Exiba os dados do sensor de umidade")
            print("2. Exiba os dados do sensor de temperatura")
            print("3. Apague os dados do sensor de umidade")
            print("4. Apague os dados do sensor de temperatura")
            print("5. Ligar bomba de água")
            print("6. Desligar bomba de água")
            print("7. Consultar previsão do tempo para definir se liga ou não a bomba de água")
            print("8. Carregar dados do banco")
            print("9. Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                exibir_dados_sensor_umidade(conn)
            elif opcao == '2':
                exibir_dados_sensor_temperatura(conn)
            elif opcao == '4':
                apagar_dados_sensor_temperatura(conn)
            elif opcao == '3':
                apagar_dados_sensor_umidade(conn)
            elif opcao == '5':
                ligar_bomba_agua()
            elif opcao == '6':
                desligar_bomba_agua()
            elif opcao == '7':
                consultar_previsao_tempo(CITY, API_KEY)
            elif opcao == '8':
                carregar_dados_do_banco(conn)
            elif opcao == '9':
                print("Saindo do programa...")
                break
            else:
                print("Opção inválida. Por favor, tente novamente.")

    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        print(f"Ocorreu um erro: {e}")

    finally:
        if conn:
            fechar_conexao(conn)
        logging.info("Conexão com o banco de dados fechada")
        client.loop_stop()

# Executar o menu principal
if __name__ == "__main__":
    load_dotenv()
    menu_principal()
