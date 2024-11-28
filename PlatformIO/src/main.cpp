#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <DHTesp.h>
#include <time.h>  // Biblioteca para obter data e hora

// Configurações de rede WiFi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// Configurações do HiveMQ Cloud
const char* mqtt_server = "91c5f1ea0f494ccebe45208ea8ffceff.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_user = "admin1";
const char* mqtt_password = "Asd123***";

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

// Intervalo de tempo para envio de mensagens de sensor
unsigned long lastHumidityMsg = 0;
unsigned long lastLightMsg = 0;
const long intervalHumidity = 20000;   // 20 segundos para temperatura e umidade
const long intervalLight = 45000;      // 45 segundos para a leitura de luz

WiFiClientSecure espClient;
PubSubClient client(espClient);

// Variáveis para medir o tempo de pressão dos botões
bool kButtonPressed = false;
unsigned long kButtonPressStart = 0;

bool pButtonPressed = false;
unsigned long pButtonPressStart = 0;

void callback(char* topic, byte* message, unsigned int length) {
  String messageTemp;

  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
  }

  if (String(topic) == pump_topic) {
    if (messageTemp == "ON") {
      digitalWrite(relayPin, HIGH);  // Liga o relé
      Serial.println("Msg recebida. Irrigação ligada! Relé ativado.");
    } else if (messageTemp == "OFF") {
      digitalWrite(relayPin, LOW);   // Desliga o relé
      Serial.println("Msg recebida. Irrigação desligada! Relé desativado.");
    }
  }
}

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

float addRandomVariation(float value, float range) {
  return value + (random(-100, 100) / 100.0) * range;
}

void sendHumidityAndTemperatureData() {
  TempAndHumidity data = dht.getTempAndHumidity();

  float simulatedTemperature = addRandomVariation(data.temperature, 0.5);
  float simulatedHumidity = addRandomVariation(data.humidity, 2.5);

  simulatedTemperature = constrain(simulatedTemperature, 20, 30);
  simulatedHumidity = constrain(simulatedHumidity, 40, 60);

  time_t now;
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Falha ao obter o tempo local");
    return;
  }

  char dateStr[11];
  char timeStr[9];
  strftime(dateStr, sizeof(dateStr), "%Y-%m-%d", &timeinfo);
  strftime(timeStr, sizeof(timeStr), "%H:%M:%S", &timeinfo);

  String payload = "{\"id_sensor\": 1, \"data_leitura\": \"" + String(dateStr) + "\", \"hora_leitura\": \"" + String(timeStr) + "\", \"temperatura\": " + String(simulatedTemperature) + ", \"umidade\": " + String(simulatedHumidity) + "}";
  
  if (client.publish(humidity_topic, payload.c_str())) {
    Serial.println("Dados de temperatura e umidade publicados:");
    Serial.println(payload);
  }
}

void sendLightData() {
  int lightIntensity = analogRead(ldrPin);
  float phEquivalent = map(lightIntensity, 0, 4095, 0, 14);
  phEquivalent = addRandomVariation(phEquivalent, 1.0);

  time_t now;
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Falha ao obter o tempo local");
    return;
  }

  char dateStr[11];
  char timeStr[9];
  strftime(dateStr, sizeof(dateStr), "%Y-%m-%d", &timeinfo);
  strftime(timeStr, sizeof(timeStr), "%H:%M:%S", &timeinfo);

  String phPayload = "{\"id_sensor\": 2, \"data_leitura\": \"" + String(dateStr) + "\", \"hora_leitura\": \"" + String(timeStr) + "\", \"ph_equivalente\": " + String(phEquivalent) + "}";
  
  if (client.publish(ph_sensor, phPayload.c_str())) {
    Serial.println("Valor equivalente de pH (LDR) publicado:");
    Serial.println(phPayload);
  }
}

void sendButtonPayload(const char* topic, const char* button, int id_sensor, unsigned long duration) {
  time_t now;
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Falha ao obter o tempo local");
    return;
  }

  char dateStr[11];
  char timeStr[9];
  strftime(dateStr, sizeof(dateStr), "%Y-%m-%d", &timeinfo);
  strftime(timeStr, sizeof(timeStr), "%H:%M:%S", &timeinfo);

  String payload = "{\"id_sensor\": " + String(id_sensor) + ", \"data_leitura\": \"" + String(dateStr) + "\", \"hora_leitura\": \"" + String(timeStr) + "\", \"duration\": " + String(duration) + "}";
  
  if (client.publish(topic, payload.c_str())) {
    Serial.println("Dados do botão " + String(button) + " publicados:");
    Serial.println(payload);
  }
}

void checkButtons() {
  bool currentKState = digitalRead(kButtonPin) == LOW;
  bool currentPState = digitalRead(pButtonPin) == LOW;

  if (currentKState && !kButtonPressed) {
    kButtonPressed = true;
    kButtonPressStart = millis();
  } else if (!currentKState && kButtonPressed) {
    kButtonPressed = false;
    unsigned long pressDuration = (millis() - kButtonPressStart) / 1000;
    if (pressDuration > 0) {
      sendButtonPayload(k_button_topic, "K", 1, pressDuration);
    }
  }

  if (currentPState && !pButtonPressed) {
    pButtonPressed = true;
    pButtonPressStart = millis();
  } else if (!currentPState && pButtonPressed) {
    pButtonPressed = false;
    unsigned long pressDuration = (millis() - pButtonPressStart) / 1000;
    if (pressDuration > 0) {
      sendButtonPayload(p_button_topic, "P", 2, pressDuration);
    }
  }
}

void setup() {
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
  }

  if (now - lastLightMsg > intervalLight) {
    lastLightMsg = now;
    sendLightData();
  }

  checkButtons();
}
