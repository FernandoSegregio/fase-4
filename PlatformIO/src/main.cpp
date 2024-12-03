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
const char* k_button_topic = "sensor/potassio";
const char* p_button_topic = "sensor/sodio";

// Pinos dos sensores e botões
const int relayPin = 27;
const int dhtPin = 23;
const int ldrPin = 34;
const int kButtonPin = 26;
const int pButtonPin = 25;

DHTesp dht;
LiquidCrystal_I2C lcd(0x27, 20, 4); // Endereço do LCD e dimensões (20x4)

// Intervalo de tempo para envio de mensagens de sensor
unsigned long lastHumidityMsg = 0;
unsigned long lastLightMsg = 0;
const long intervalHumidity = 20000;   // 20 segundos para temperatura e umidade
const long intervalLight = 45000;      // 45 segundos para leitura de luz

WiFiClientSecure espClient;
PubSubClient client(espClient);

// Variáveis globais para valores recentes
float lastTemperature = -1;
float lastHumidity = -1;
float lastPH = -1;

// Variáveis para armazenar os últimos valores exibidos no LCD
float displayedTemperature = -1;
float displayedHumidity = -1;
float displayedPH = -1;
bool displayedRelayState = false;

// Variáveis para medir o tempo de pressão dos botões
bool kButtonPressed = false;
unsigned long kButtonPressStart = 0;

bool pButtonPressed = false;
unsigned long pButtonPressStart = 0;

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

// Função para atualizar o LCD somente se houver mudanças
void updateLCD() {
  bool relayState = digitalRead(relayPin);
  bool needUpdate = false;

  // Verifica mudanças nos valores antes de atualizar o LCD
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

  pinMode(kButtonPin, INPUT_PULLUP);
  pinMode(pButtonPin, INPUT_PULLUP);

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

  // Atualiza sensores em intervalos definidos
  if (now - lastHumidityMsg > intervalHumidity) {
    lastHumidityMsg = now;
    sendHumidityAndTemperatureData();
  }

  if (now - lastLightMsg > intervalLight) {
    lastLightMsg = now;
    sendLightData();
  }

  // Atualiza o LCD somente quando necessário
  updateLCD();
}
