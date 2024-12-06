#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <DHTesp.h>
#include <time.h> // Biblioteca para obter data e hora

// Configurações de rede WiFi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// Configurações do HiveMQ Cloud
const char* mqtt_server = "91c5f1ea0f494ccebe45208ea8ffceff.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_user = "FARM_TECH";
const char* mqtt_password = "Pato1234";

// Tópicos MQTT
const char* pump_topic = "sensor/bomba";
const char* humidity_topic = "sensor/umidade";
const char* temperature_topic = "sensor/temperatura";
const char* ph_sensor = "sensor/ph";

// Pinos dos sensores
const int relayPin = 27;
const int dhtPin = 23;
const int ldrPin = 34;

DHTesp dht;
LiquidCrystal_I2C lcd(0x27, 20, 4); // Endereço do LCD e dimensões (20x4)

// Intervalos de tempo
unsigned long lastHumidityMsg = 0;
unsigned long lastLightMsg = 0;
const long intervalHumidity = 20000;   // 20 segundos para temperatura e umidade
const long intervalLight = 45000;      // 45 segundos para leitura de pH

WiFiClientSecure espClient;
PubSubClient client(espClient);

// Variáveis globais para valores recentes
float lastTemperature = -1;
float lastHumidity = -1;
float lastPH = -1;

// Variáveis para valores exibidos no LCD
float displayedTemperature = -1;
float displayedHumidity = -1;
float displayedPH = -1;
bool displayedRelayState = false;

// Função para adicionar variação randômica
float addRandomVariation(float value, float range) {
  return value + (random(-100, 100) / 100.0) * range;
}

// Função para conectar ao Wi-Fi
void setup_wifi() {
  Serial.println("Conectando ao Wi-Fi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado");
  Serial.println("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

// Função para reconectar ao MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando conectar ao MQTT...");
    espClient.setInsecure();

    if (client.connect("ESP32Client", mqtt_user, mqtt_password)) {
      Serial.println("Conectado ao broker MQTT!");
      client.subscribe(pump_topic);
    } else {
      Serial.print("Falha na conexão, rc=");
      Serial.print(client.state());
      Serial.println(" Tentando novamente em 5 segundos");
      delay(5000);
    }
  }
}

// Função para obter a data atual
String getCurrentDate() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "2024-01-01"; // Data padrão em caso de erro
  }
  char buffer[11];
  strftime(buffer, sizeof(buffer), "%Y-%m-%d", &timeinfo);
  return String(buffer);
}

// Função para obter a hora atual
String getCurrentTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "00:00"; // Hora padrão em caso de erro
  }
  char buffer[6];
  strftime(buffer, sizeof(buffer), "%H:%M", &timeinfo);
  return String(buffer);
}

// Função para enviar dados de umidade para o MQTT
void sendHumidityDataToMQTT() {
  String payload = "{";
  payload += "\"id_sensor\":1,";
  payload += "\"data_leitura\":\"" + getCurrentDate() + "\",";
  payload += "\"hora_leitura\":\"" + getCurrentTime() + "\",";
  payload += "\"Valor\":" + String(lastHumidity);
  payload += "}";

  client.publish(humidity_topic, payload.c_str());
  Serial.println("Enviado para MQTT: " + payload);
}

// Função para enviar dados de temperatura para o MQTT
void sendTemperatureDataToMQTT() {
  String payload = "{";
  payload += "\"id_sensor\":2,";
  payload += "\"data_leitura\":\"" + getCurrentDate() + "\",";
  payload += "\"hora_leitura\":\"" + getCurrentTime() + "\",";
  payload += "\"Valor\":" + String(lastTemperature);
  payload += "}";

  client.publish(temperature_topic, payload.c_str());
  Serial.println("Enviado para MQTT: " + payload);
}

// Função para enviar dados de pH para o MQTT
void sendPHDataToMQTT() {
  String payload = "{";
  payload += "\"id_sensor\":3,";
  payload += "\"data_leitura\":\"" + getCurrentDate() + "\",";
  payload += "\"hora_leitura\":\"" + getCurrentTime() + "\",";
  payload += "\"Valor\":" + String(lastPH);
  payload += "}";

  client.publish(ph_sensor, payload.c_str());
  Serial.println("Enviado para MQTT: " + payload);
}

// Função de callback para mensagens MQTT
void callback(char* topic, byte* payload, unsigned int length) {
  String messageTemp;

  for (unsigned int i = 0; i < length; i++) {
    messageTemp += (char)payload[i];
  }

  Serial.println("Mensagem recebida no tópico: " + String(topic));
  Serial.println("Conteúdo: " + messageTemp);

  if (String(topic) == pump_topic) {
    if (messageTemp == "ON") {
      digitalWrite(relayPin, HIGH);  // Liga o relé
      Serial.println("Irrigação ligada!");
    } else if (messageTemp == "OFF") {
      digitalWrite(relayPin, LOW);   // Desliga o relé
      Serial.println("Irrigação desligada!");
    }
  }
}

// Função para enviar dados de temperatura e umidade
void sendHumidityAndTemperatureData() {
  TempAndHumidity data = dht.getTempAndHumidity();

  lastTemperature = constrain(addRandomVariation(data.temperature, 0.5), 20, 30);
  lastHumidity = constrain(addRandomVariation(data.humidity, 2.5), 40, 60);

  Serial.println("Temp: " + String(lastTemperature) + " Umidade: " + String(lastHumidity));
}

// Função para enviar dados de luz e pH
void sendLightData() {
  int lightIntensity = analogRead(ldrPin);
  lastPH = constrain(map(lightIntensity, 0, 4095, 0, 14) + random(-1, 1), 0, 14);

  Serial.println("pH: " + String(lastPH));
}

// Função para atualizar o LCD
void updateLCD() {
  bool relayState = digitalRead(relayPin);
  bool needUpdate = false;

  if (lastTemperature != displayedTemperature) {
    displayedTemperature = lastTemperature;
    needUpdate = true;
  }
  if (lastHumidity != displayedHumidity) {
    displayedHumidity = lastHumidity;
    needUpdate = true;
  }
  if (lastPH != displayedPH) {
    displayedPH = lastPH;
    needUpdate = true;
  }
  if (relayState != displayedRelayState) {
    displayedRelayState = relayState;
    needUpdate = true;
  }

  if (needUpdate) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Temp: ");
    lcd.print(displayedTemperature);
    lcd.print(" C");

    lcd.setCursor(0, 1);
    lcd.print("Umidade: ");
    lcd.print(displayedHumidity);
    lcd.print(" %");

    lcd.setCursor(0, 2);
    lcd.print("pH: ");
    lcd.print(displayedPH);

    lcd.setCursor(0, 3);
    lcd.print("Irrigacao: ");
    lcd.print(displayedRelayState ? "Ligada" : "Desligada");
  }
}

void setup() {
  Wire.begin(18, 19); // SDA = 18, SCL = 19
  Serial.begin(115200);

  setup_wifi();
  configTime(-3 * 3600, 0, "pool.ntp.org", "time.nist.gov");

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  reconnect();

  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);

  dht.setup(dhtPin, DHTesp::DHT22);

  lcd.init();
  lcd.backlight();
  lcd.print("Iniciando...");
  delay(2000);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();

  if (now - lastHumidityMsg > intervalHumidity) {
    lastHumidityMsg = now;
    sendHumidityAndTemperatureData();
    sendHumidityDataToMQTT();
    sendTemperatureDataToMQTT();
  }

  if (now - lastLightMsg > intervalLight) {
    lastLightMsg = now;
    sendLightData();
    sendPHDataToMQTT();
  }

  updateLCD();
}