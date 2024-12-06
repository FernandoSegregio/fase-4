import logging
import paho.mqtt.client as mqtt
import ssl
import streamlit as st
from dotenv import load_dotenv
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from scripts.connect_db import conectar_banco, fechar_conexao
from scripts.setup_db import setup_banco_dados
from scripts.consulta_banco import carregar_dados_umidade
from PIL import Image, ImageDraw
from typing import Tuple
import numpy as np
import pandas as pd
import plotly.express as px

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error


# Configuração de layout da página
st.set_page_config(page_title="🚜 FarmTech - Sistema Inteligente de Gestão Agrícola", layout="wide")

def make_rounded_image(image, radius=50):
    # Garantir que a imagem seja quadrada (ou ajustar automaticamente)
    size = image.size
    mask = Image.new("L", size, 0)  # Criar máscara de luminosidade (L)
    draw = ImageDraw.Draw(mask)
    
    # Criar retângulo arredondado como máscara
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    
    # Adicionar canal alfa para suportar transparência
    rounded_image = Image.new("RGBA", size)
    rounded_image.paste(image, (0, 0), mask=mask)
    
    return rounded_image

# Carregar a imagem e aplicar bordas arredondadas
logo = Image.open('assets/farm-tech-logo.png').convert("RGBA")
logo_rounded = make_rounded_image(logo, radius=50)

# Exibir a imagem com bordas arredondadas no menu lateral
st.sidebar.image(logo_rounded, caption="FarmTech Solutions", width=286)

# CSS customizado para os botões
st.markdown("""
    <style>
    .stButton>button {
        background-color: #39ff14;
        color: #000080;
        font-size: 16px;
        border: none;
        border-radius: 5px;
        margin-bottom: 6px;
        cursor: pointer;
        width: 286px;
    }
    .stButton>button:hover {
        background-color: #2ecc71;
        color: #000080 !important;
    }
    .stButton>button:focus {
        background-color: #000080;
        color: #39ff14 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Configurações globais
load_dotenv()
mqtt_server = st.secrets["mqtt"]["server"]
mqtt_port = st.secrets["mqtt"]["port"]
mqtt_user = st.secrets["mqtt"]["user"]
mqtt_password = st.secrets["mqtt"]["password"]
humidity_topic = "sensor/umidade"
pump_topic = "sensor/bomba"

API_KEY = 'c60a4792ccbe5983e113c048825b78fb'
CITY = 'Juiz de Fora'
PREDICT_DAYS = 7

# Logging
logging.basicConfig(
    filename='app.log', level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# MQTT Client
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.connect(mqtt_server, mqtt_port, 60)
client.loop_start()

# Funções
def ligar_bomba_agua():
    client.publish(pump_topic, "ON")
    st.success("Comando enviado para ligar a bomba de água.")

def desligar_bomba_agua():
    client.publish(pump_topic, "OFF")
    st.success("Comando enviado para desligar a bomba de água.")

# Configurações de API
API_KEY = 'c60a4792ccbe5983e113c048825b78fb'
CITY = 'Juiz de Fora'
PREDICT_DAYS = 7

# Funções de Preparação de Imagem
def make_rounded_image(image, radius=50):
    """Cria imagem com bordas arredondadas"""
    size = image.size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    
    rounded_image = Image.new("RGBA", size)
    rounded_image.paste(image, (0, 0), mask=mask)
    
    return rounded_image

# Funções de Previsão de Precipitação
def preparar_dados_precipitacao(dados_climatologicos):
    """Prepara dados climatológicos para treinamento do modelo"""
    precipitacao = dados_climatologicos['properties']['parameter']['PRECTOTCORR']
    temp_max = dados_climatologicos['properties']['parameter']['T2M_MAX']
    temp_min = dados_climatologicos['properties']['parameter']['T2M_MIN']
    
    df = pd.DataFrame({
        'data': list(precipitacao.keys()),
        'precipitacao': list(precipitacao.values()),
        'temp_max': list(temp_max.values()),
        'temp_min': list(temp_min.values())
    })
    
    df['data'] = pd.to_datetime(df['data'], format='%Y%m%d')
    df['mes'] = df['data'].dt.month
    df['dia_ano'] = df['data'].dt.dayofyear
    df['precipitacao_proxdia'] = df['precipitacao'].shift(-1)
    df.dropna(inplace=True)
    
    return df

def treinar_modelo_precipitacao(df):
    """Treina modelo de precipitação"""
    features = ['temp_max', 'temp_min', 'mes', 'dia_ano']
    X = df[features]
    y = df['precipitacao_proxdia']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    modelo = RandomForestRegressor(
        n_estimators=200, 
        random_state=42, 
        min_samples_split=5
    )
    modelo.fit(X_train_scaled, y_train)
    
    y_pred = modelo.predict(X_test_scaled)
    
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    return modelo, scaler, {
        'MAE': mae, 
        'MSE': mse, 
        'RMSE': rmse
    }

def visualizar_predicoes(df, modelo, scaler):
    """Cria visualizações das predições de precipitação"""
    features = ['temp_max', 'temp_min', 'mes', 'dia_ano']
    X = df[features].iloc[-7:]
    X_scaled = scaler.transform(X)
    
    predicoes = modelo.predict(X_scaled)
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['data'].iloc[-7:], predicoes, marker='o', label='Precipitação Predita')
    plt.plot(df['data'].iloc[-7:], df['precipitacao'].iloc[-7:], marker='x', label='Precipitação Real')
    plt.title('Predição de Precipitação')
    plt.xlabel('Data')
    plt.ylabel('Precipitação (mm)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return plt, predicoes

def main_predicao_chuva(dados_climatologicos):
    """Função principal para predição de precipitação"""
    try:
        df = preparar_dados_precipitacao(dados_climatologicos)
        modelo, scaler, metricas = treinar_modelo_precipitacao(df)
        
        st.subheader("🌧️ Modelo de Predição de Precipitação")
        st.write("Métricas de Performance:")
        st.write(f"- Erro Absoluto Médio (MAE): {metricas['MAE']:.2f} mm")
        st.write(f"- Erro Quadrático Médio (MSE): {metricas['MSE']:.2f} mm²")
        st.write(f"- Raiz do Erro Quadrático Médio (RMSE): {metricas['RMSE']:.2f} mm")
        
        fig, predicoes = visualizar_predicoes(df, modelo, scaler)
        st.pyplot(fig)
        
        st.subheader("Previsão de Precipitação para Próximos Dias")
        for i, pred in enumerate(predicoes, 1):
            st.write(f"Dia {i}: {pred:.2f} mm de precipitação prevista")
        
        return predicoes
    
    except Exception as e:
        st.error(f"Erro na predição de chuva: {e}")
        return None

# Funções de API e Consultas
def get_city_coordinates(city: str, api_key: str) -> Tuple[float, float]:
    """Obtém coordenadas geográficas da cidade"""
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        
        return lat, lon
        
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição: {str(e)}")
        return None, None

def consultar_climatologia(city: str):
    """Consulta dados climatológicos pela API da NASA"""
    try:
        # Obter coordenadas da cidade
        lat, lon = get_city_coordinates(city, API_KEY)
        
        if lat is None or lon is None:
            st.error("Não foi possível obter coordenadas.")
            return None
        
        # URL da API NASA POWER
        url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        
        # Parâmetros da requisição
        params = {
            "start": "2020",
            "end": "2023",
            "latitude": lat,
            "longitude": lon,
            "community": "RE",
            "parameters": "PRECTOTCORR,T2M_MAX,T2M_MIN",
            "format": "JSON"
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extrair dados
        precipitacao = data['properties']['parameter']['PRECTOTCORR']
        temp_max = data['properties']['parameter']['T2M_MAX']
        temp_min = data['properties']['parameter']['T2M_MIN']
        
        # Calcular estatísticas
        total_precip = sum(precipitacao.values())
        media_precip = total_precip / len(precipitacao)
        
        # Criar visualizações
        datas = [datetime.strptime(d, '%Y%m%d') for d in precipitacao.keys()]
        
        # Figura com 2 subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Gráfico de precipitação
        ax1.plot(datas, list(precipitacao.values()), 'b-', linewidth=1)
        ax1.fill_between(datas, list(precipitacao.values()), alpha=0.3)
        ax1.set_title('Precipitação Diária')
        ax1.set_ylabel('Precipitação (mm)')
        ax1.grid(True)
        
        # Gráfico de temperaturas
        ax2.plot(datas, list(temp_max.values()), 'r-', label='Máxima')
        ax2.plot(datas, list(temp_min.values()), 'b-', label='Mínima')
        ax2.fill_between(datas, list(temp_min.values()), list(temp_max.values()), alpha=0.2)
        ax2.set_title('Temperaturas Máxima e Mínima')
        ax2.set_ylabel('Temperatura (°C)')
        ax2.legend()
        ax2.grid(True)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Exibir gráficos no Streamlit
        st.subheader("Análise Climatológica")
        st.write(f"Total de precipitação: {total_precip:.2f} mm")
        st.write(f"Média diária de precipitação: {media_precip:.2f} mm/dia")
        st.pyplot(fig)
        
        return data
        
    except Exception as e:
        st.error(f"Erro na consulta climatológica: {e}")
        return None

def consultar_previsao_tempo():
    """Consulta previsão do tempo pela OpenWeatherMap"""
    link_rain = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(link_rain)
        
        if response.status_code == 200:
            data = response.json()
            previsao = data['list']
            
            # Criar DataFrame para melhor visualização
            df_previsao = pd.DataFrame([
                {
                    'data': datetime.fromtimestamp(item['dt']),
                    'temperatura': item['main']['temp'],
                    'probabilidade_chuva': item.get('pop', 0) * 100
                } for item in previsao[:PREDICT_DAYS * 8]
            ])
            
            # Plotar previsão
            plt.figure(figsize=(12, 6))
            plt.plot(df_previsao['data'], df_previsao['temperatura'], marker='o', label='Temperatura')
            plt.bar(df_previsao['data'], df_previsao['probabilidade_chuva'], alpha=0.3, label='Prob. Chuva')
            plt.title(f'Previsão do Tempo para {CITY}')
            plt.xlabel('Data')
            plt.ylabel('Temperatura (°C) / Probabilidade Chuva (%)')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            st.subheader("🌦️ Previsão do Tempo")
            st.pyplot(plt)
            
            # Verificar chance de chuva
            chuva_prevista = df_previsao[df_previsao['probabilidade_chuva'] > 30]
            if not chuva_prevista.empty:
                st.warning(f"Atenção: {len(chuva_prevista)} dias com alta chance de chuva")
            
            return data
        else:
            st.error(f"Erro na consulta. Status: {response.status_code}")
            return None
    
    except Exception as e:
        st.error(f"Erro na consulta de previsão: {e}")
        return None


def get_city_coordinates(city: str, api_key: str) -> Tuple[float, float]:

    logging.info(f"Buscando coordenadas para cidade: {city}")
    
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        logging.info(f"Dados recebidos para {city}: {data}")
        
        if 'coord' not in data:
            raise KeyError(f"Coordenadas não encontradas para {city}")
            
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        
        logging.info(f"Coordenadas obtidas: lat={lat}, lon={lon}")
        return lat, lon
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição: {str(e)}")
        raise Exception(f"Erro ao obter coordenadas: {str(e)}")
    
    except KeyError as e:
        logging.error(f"Erro ao processar dados: {str(e)}")
        raise Exception(f"Dados inválidos na resposta: {str(e)}")


def consultar_climatologia(city: str):
    try:
        # Obter coordenadas da cidade
        lat, lon = get_city_coordinates(city, API_KEY)
        
        # URL da API NASA POWER
        url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        
        # Parâmetros da requisição
        params = {
            "start": "2020",
            "end": "2023",
            "latitude": lat,
            "longitude": lon,
            "community": "RE",
            "parameters": "PRECTOTCORR,T2M_MAX,T2M_MIN",
            "format": "JSON"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extrair dados
        precipitacao = data['properties']['parameter']['PRECTOTCORR']
        temp_max = data['properties']['parameter']['T2M_MAX']
        temp_min = data['properties']['parameter']['T2M_MIN']
        
        # Calcular estatísticas
        total_precip = sum(precipitacao.values())
        media_precip = total_precip / len(precipitacao)
        
        # Exibir estatísticas
        st.subheader("Dados de Precipitação")
        st.write(f"Total de precipitação no período: {total_precip:.2f} mm")
        st.write(f"Média diária de precipitação: {media_precip:.2f} mm/dia")
        
        # Criar gráficos
        datas = [datetime.strptime(d, '%Y%m%d') for d in precipitacao.keys()]
        
        # Figura com 2 subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Gráfico de precipitação
        ax1.plot(datas, list(precipitacao.values()), 'b-', linewidth=1)
        ax1.fill_between(datas, list(precipitacao.values()), alpha=0.3)
        ax1.set_title('Precipitação Diária')
        ax1.set_ylabel('Precipitação (mm)')
        ax1.grid(True)
        
        # Gráfico de temperaturas
        ax2.plot(datas, list(temp_max.values()), 'r-', label='Máxima')
        ax2.plot(datas, list(temp_min.values()), 'b-', label='Mínima')
        ax2.fill_between(datas, list(temp_min.values()), list(temp_max.values()), alpha=0.2)
        ax2.set_title('Temperaturas Máxima e Mínima')
        ax2.set_ylabel('Temperatura (°C)')
        ax2.legend()
        ax2.grid(True)
        
        # Ajustes finais
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Exibir no Streamlit
        st.pyplot(fig)
        
        return data
        
    except Exception as e:
        st.error(f"Erro ao consultar dados climatológicos: {str(e)}")
        return None

def plotar_grafico_previsao(previsao):
    datas = [datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S') for item in previsao]
    temperaturas = [item['main']['temp'] for item in previsao]
    chuva = [item.get('pop', 0) * 100 for item in previsao]
    
    plt.figure(figsize=(8, 4))
    plt.plot(datas, temperaturas, label='Temperatura (°C)', color='orange')
    plt.bar(datas, chuva, label='Probabilidade de Chuva (%)', color='blue', alpha=0.5)
    plt.xlabel('Data e Hora')
    plt.ylabel('Valores')
    plt.title('Previsão do Tempo')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

def predizer_necessidade_irrigacao(dados_clima):
    try:
        # Extrair dados
        precipitacao = dados_clima['properties']['parameter']['PRECTOTCORR']
        temp_max = dados_clima['properties']['parameter']['T2M_MAX']
        temp_min = dados_clima['properties']['parameter']['T2M_MIN']
        
        # Criar DataFrame
        df = pd.DataFrame({
            'data': precipitacao.keys(),
            'precipitacao': precipitacao.values(),
            'temp_max': temp_max.values(),
            'temp_min': temp_min.values()
        })
        
        # Target
        df['necessita_irrigacao'] = ((df['precipitacao'] < 5) & (df['temp_max'] > 28)).astype(int)
        
        # Features
        X = df[['precipitacao', 'temp_max', 'temp_min']]
        y = df['necessita_irrigacao']
        
        # Split e treino
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        modelo = RandomForestClassifier(n_estimators=100, random_state=42)
        modelo.fit(X_train_scaled, y_train)
        
        # Últimos dados para predição
        ultima_precipitacao = list(precipitacao.values())[-1]
        ultima_temp_max = list(temp_max.values())[-1]
        ultima_temp_min = list(temp_min.values())[-1]
        
        X_pred = np.array([[ultima_precipitacao, ultima_temp_max, ultima_temp_min]])
        X_pred_scaled = scaler.transform(X_pred)
        
        necessita_irrigacao = modelo.predict(X_pred_scaled)[0]
        probabilidade = modelo.predict_proba(X_pred_scaled)[0][1]
        
        score = modelo.score(X_test_scaled, y_test)
        
        # Exibir resultados
        st.subheader("Modelo de Previsão de Irrigação")
        st.write(f"Acurácia do modelo: {score:.2f}")
        
        if necessita_irrigacao:
            st.warning(f"Sistema recomenda irrigação (Probabilidade: {probabilidade:.2f})")
            if probabilidade > 0.7:
                ligar_bomba_agua()
        else:
            st.success(f"Irrigação não necessária no momento (Probabilidade: {probabilidade:.2f})")
            if probabilidade < 0.3:
                desligar_bomba_agua()
                
    except Exception as e:
        st.error(f"Erro ao criar modelo: {str(e)}")

def exibir_dados_sensor_umidade(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id_leitura_umidade, id_sensor_umidade, data_leitura, hora_leitura, valor_umidade_leitura FROM LEITURA_SENSOR_UMIDADE ORDER BY hora_leitura DESC")
    resultados = cursor.fetchall()
    
    if resultados:
        # Criar DataFrame
        df = pd.DataFrame(resultados, columns=[
            'ID Leitura',
            'ID Sensor',
            'Data',
            'Hora',
            'Umidade (%)'
        ])
        
        # Formatar data e hora
        df['Hora'] = pd.to_datetime(df['Hora']).dt.strftime('%H:%M:%S')
        df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%d/%m/%Y')
        
        # Função de estilo para destacar valores fora do limite
        def style_umidade(val):
            if pd.isna(val):
                return ''
            try:
                val = float(val)
                if val < 45 or val > 55:
                    return 'color: red; font-weight: bold'
                return 'color: green; font-weight: normal'
            except:
                return ''
        
        # Aplicar estilo
        styled_df = df.style\
            .applymap(style_umidade, subset=['Umidade (%)'])\
            .format({'Umidade (%)': '{:.2f}'})
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Média de Umidade", 
                f"{df['Umidade (%)'].mean():.2f}%",
                delta_color="inverse"
            )
        with col2:
            ultimo_valor = df['Umidade (%)'].iloc[0]
            status = "🔴" if (ultimo_valor < 45 or ultimo_valor > 55) else "🟢"
            st.metric(
                "Última Leitura",
                f"{ultimo_valor:.2f}% {status}"
            )
        with col3:
            valores_fora = len(df[(df['Umidade (%)'] < 45) | (df['Umidade (%)'] > 55)])
            st.metric("Leituras Fora do Limite", valores_fora)
        
        # Tabela
        st.write("### Histórico de Leituras")
        st.dataframe(styled_df, width=1000)
        
        # Gráfico com limites
        fig = px.line(df, x='Hora', y='Umidade (%)', title='Monitoramento de Umidade')
        fig.add_hline(y=55, line_dash="dash", line_color="red")
        fig.add_hline(y=45, line_dash="dash", line_color="red")
        st.plotly_chart(fig)
        
    else:
        st.info("Nenhum dado encontrado para o sensor de umidade.")
    
    cursor.close()

def apagar_dados_sensor_umidade(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM LEITURA_SENSOR_UMIDADE")
    conn.commit()
    st.success("Dados do sensor de umidade apagados com sucesso.")
    cursor.close()

# Inicializar estado
if "selected_button" not in st.session_state:
    st.session_state.selected_button = "Exibir Dados do Sensor de Umidade"


menu_options = [
    "Exibir Dados do Sensor de Umidade",
    "Ligar Bomba de Água",
    "Desligar Bomba de Água",
    "Consultar Previsão do Tempo",
    "Predição de Irrigação",
    "Previsão de Precipitação", 
    "Configuração Inicial do Banco",
    "Simulador Wokwi"
]

# Botões no menu lateral
for option in menu_options:
    if st.sidebar.button(option):
        st.session_state.selected_button = option

# Conexão com o banco de dados
conn = conectar_banco()
if not conn:
    st.error("Erro ao conectar ao banco de dados.")
else:
    selected = st.session_state.selected_button

    if selected == "Exibir Dados do Sensor de Umidade":
        st.title("Exibir Dados do Sensor de Umidade")
        exibir_dados_sensor_umidade(conn)
    
    elif selected == "Ligar Bomba de Água":
        st.title("Ligar Bomba de Água")
        ligar_bomba_agua()
    
    elif selected == "Desligar Bomba de Água":
        st.title("Desligar Bomba de Água")
        desligar_bomba_agua()
    
    elif selected == "Consultar Previsão do Tempo":
        st.title("Consultar Previsão do Tempo")
        previsao = consultar_climatologia(CITY)
    
    elif selected == "Apagar Dados do Sensor de Umidade":
        st.title("Apagar Dados do Sensor de Umidade")
        apagar_dados_sensor_umidade(conn)
    
    elif selected == "Configuração Inicial do Banco":
        st.title("Configuração Inicial do Banco")
        setup_banco_dados(conn)
        st.success("Banco de dados configurado com sucesso.")

    elif selected == "Previsão de Precipitação":
        st.subheader("Predição de Precipitação")
        dados_clima = consultar_climatologia(CITY)
        if dados_clima:
            main_predicao_chuva(dados_clima)

    elif selected == "Predição de Irrigação":
        st.title("Predição de Irrigação")
        dados_clima = consultar_climatologia(CITY)
        if dados_clima:
            predizer_necessidade_irrigacao(dados_clima)

    elif selected == "Simulador Wokwi":
        st.title("Simulador Wokwi")
        wokwi_url = "https://wokwi.com/projects/416454855235409921"
        st.markdown(f"""
            <iframe 
                src="{wokwi_url}" 
                width="100%" 
                height="600" 
                style="border:none;"></iframe>
        """, unsafe_allow_html=True)

    

fechar_conexao(conn)
client.loop_stop()

