import os
import json
import logging
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from scripts.connect_db import conectar_banco, fechar_conexao
from scripts.setup_db import setup_banco_dados
from scripts.consulta_banco import carregar_dados_db
from scripts.consulta_banco import inserir_leitura_umidade, inserir_leitura_temperatura, inserir_leitura_ph

# Configuração de MQTT e Tópicos
mqtt_server = "91c5f1ea0f494ccebe45208ea8ffceff.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_user = "admin1"
mqtt_password = "Asd123***"
humidity_topic = "sensor/umidade"
ph_sensor = "sensor/ph"
k_button_topic = "sensor/potassio"
p_button_topic = "sensor/sodio"
pump_topic = "sensor/bomba"

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
    client.subscribe(ph_sensor)
    client.subscribe(k_button_topic)
    client.subscribe(p_button_topic)

client.on_connect = on_connect
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port, 60)
client.loop_start()

# Função para ligar a bomba de água manualmente
def ligar_bomba_agua():
    client.publish(pump_topic, "ON")
    print("Comando 'ON' enviado para ligar a bomba de água.")

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

# Função para carregar dados do banco de dados
def carregar_dados_do_banco(conn):
    try:
        df = carregar_dados_db(conn, logging)
        if df is not None and not df.empty:
            print("Dados carregados com sucesso:")
            print(df)
        else:
            print("Não foi possível carregar dados do banco.")
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
            print("3. Apague os dados do sensor de temperatura")
            print("4. Ligar bomba de água")
            print("5. Desligar bomba de água")
            print("6. Carregar dados do banco")
            print("7. Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                exibir_dados_sensor_umidade(conn)
            elif opcao == '2':
                exibir_dados_sensor_temperatura(conn)
            elif opcao == '3':
                apagar_dados_sensor_temperatura(conn)
            elif opcao == '4':
                ligar_bomba_agua()
            elif opcao == '5':
                desligar_bomba_agua()
            elif opcao == '6':
                carregar_dados_do_banco(conn)
            elif opcao == '7':
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
