/*#include <PubSubClient.h>
#include <WiFi.h>

WiFiClient espClient;
PubSubClient client(espClient);

const char* ssid = "ISR-Robots";
const char* mqttServer = "postman.cloudmqtt.com";
const int mqttPort = 14877;
const char* mqttUser = "pkmtmkxo";
const char* mqttPassword = "cY9ZBQTUMmKs";

int inPin = 32;
int ledPinV = 14;
int ledPinG = 13;
int val = 0;

void setup() {
  Serial.begin(115200);
  pinMode (inPin, INPUT);
  pinMode (ledPinG, OUTPUT);
  pinMode (ledPinV, OUTPUT);

  configuracoes_rede();
}

void loop() {
  static uint32_t beat = 0;
  static uint32_t beat_ant = 0;
  if (millis() - beat > 500) {
    if (millis() - beat < 2500) {
      digitalWrite(ledPinG, HIGH);
    }
    else {
      val = analogRead(inPin);
      digitalWrite (ledPinG, LOW);
      Serial.println(val);
      char result[16];
      itoa(val, result, 10);
      client.publish("esp/water", result);
      client.subscribe("esp/water");
      erro_rede();
      beat = millis();
      if (beat_ant > beat)
        beat = 0;
      else
        beat_ant = beat;
    }
  }
}

void configuracoes_rede() {
  digitalWrite (ledPinV, HIGH);
  digitalWrite (ledPinG, LOW);
  static uint32_t beat = 0;
  static uint32_t beat_ant = 0;
  WiFi.disconnect();
  WiFi.begin(ssid);
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - beat > 500) {
      Serial.print("Connecting to WiFi:");
      Serial.println(ssid);
    }
    beat = millis();
    if (beat_ant > beat)
      beat = 0;
    else
      beat_ant = beat;
  }
  Serial.println("Connected to the WiFi network");
  Serial.println("");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite (ledPinG, HIGH);
  configuracoes_mqtt();
}

void configuracoes_mqtt() {
  digitalWrite (ledPinV, HIGH);
  digitalWrite (ledPinG, HIGH);
  static uint32_t beat = 0;
  static uint32_t beat_ant = 0;

  client.setServer(mqttServer, mqttPort);

  while (!client.connected()) {
    Serial.println("Passei por aqui2!");
    Serial.println("Connecting to MQTT…");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str(), mqttUser, mqttPassword )) {
      Serial.println("connected");
    } else {
      if (millis() - beat > 2000) {
        Serial.print("failed with state ");
        Serial.print(client.state());

        beat = millis();
        if (beat_ant > beat)
          beat = 0;
        else
          beat_ant = beat;
      }
    }
  }
  Serial.println("Passei por aqui1!");
  client.publish("esp/connect", "water");
  client.subscribe("esp/connect");

  digitalWrite (ledPinV, LOW);
  digitalWrite (ledPinG, LOW);
}

void erro_rede() {
  Serial.println("Passei por aqui4!");
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Erro na conexão wifi!");
    configuracoes_rede();
  }
  else if (!client.connected()) {
    Serial.println("Erro na conexão MQTT!");
    configuracoes_mqtt();
  }
}
*/

#include <PubSubClient.h>
#include <WiFi.h>

WiFiClient espClient;
PubSubClient client(espClient);

const char* ssid = "IS3L";
const char* password = "ErasmusKustar";
//const char* mqttServer = "postman.cloudmqtt.com";
const char* mqttServer = "10.231.234.184";
const int mqttPort = 1883;
//const int mqttPort = 14877;
const char* mqttUser = "pkmtmkxo";
const char* mqttPassword = "cY9ZBQTUMmKs";

int inPin = 32;
int ledPinV = 14;
int ledPinG = 13;
int val = 0;
int val_ant = 1;

void setup() {
  Serial.begin(115200);
  pinMode(inPin, INPUT);
  pinMode (ledPinG, OUTPUT);
  pinMode (ledPinV, OUTPUT);

  configuracoes_rede();
  configuracoes_mqtt();
}

void loop() {
  static uint32_t beat = 0;
  static uint32_t beat_ant = 0;
  if (millis() - beat > 500) {
    if (millis() - beat < 1000) {
      digitalWrite (ledPinG, HIGH);
    }
    else {
      val = analogRead(inPin);
      Serial.print("Valor lido: ");
      Serial.println(val);
      if (val != 0)
        val = 1;
      else
        val = 0;
      if (val != val_ant) {
        Serial.println("Entrei no ciclo");
        digitalWrite (ledPinG, LOW);
        erro_rede();
        Serial.println(val);
        char result[16];
        itoa(val, result, 10);
        Serial.print("MQTT connection state antes do publish: ");
        Serial.println(client.state());
        client.publish("esp/water", result);
        val_ant = val;
      }
      beat = millis();
      if (beat_ant > beat)
        beat = 0;
      else
        beat_ant = beat;
      Serial.print("MQTT connection state: ");
      Serial.println(client.state());
    }
  }
}

void configuracoes_rede() {
  digitalWrite (ledPinV, HIGH);
  digitalWrite (ledPinG, LOW);
  static uint32_t beat = 0;
  static uint32_t beat_ant = 0;
  WiFi.disconnect();
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - beat > 500) {
      Serial.print("Connecting to WiFi:");
      Serial.println(ssid);
    }
    beat = millis();
    if (beat_ant > beat)
      beat = 0;
    else
      beat_ant = beat;
  }
  Serial.println("Connected to the WiFi network");
  Serial.println("");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite (ledPinV, HIGH);
  digitalWrite (ledPinG, HIGH);
  //configuracoes_mqtt();
}

void configuracoes_mqtt() {
  digitalWrite (ledPinV, HIGH);
  digitalWrite (ledPinG, HIGH);
  static uint32_t beat = 0;
  static uint32_t beat_ant = 0;

  client.setServer(mqttServer, mqttPort);
  
  int contador = 0;
  while (!client.connected()) {
    Serial.println("Passei por aqui2!");
    Serial.println("Connecting to MQTT…");
    String clientId = "ESP32Client-";
    //clientId += String(random(0xffff), HEX);
    if (client.connect("water")) {
    //if (client.connect("water", mqttUser, mqttPassword )) {
      Serial.println("connected");
    } else {
      if (millis() - beat > 2000) {
        Serial.print("failed with state ");
        Serial.print(client.state());
        beat = millis();
        if (beat_ant > beat)
          beat = 0;
        else
          beat_ant = beat;
        if (contador > 2) {
          ESP.restart();
        }
        contador++;
        Serial.print("Contador: ");
        Serial.println(contador);        
      }
      Serial.print("Passei pela espera e: ");
      Serial.println(millis() - beat); 
    }
  }
  Serial.println("Passei por aqui1!");
  client.publish("esp/connect", "water");
  //client.subscribe("esp/connect");

  digitalWrite (ledPinV, LOW);
  digitalWrite (ledPinG, LOW);
}

void erro_rede() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Erro na conexão wifi!");
    configuracoes_rede();
  }
  if (!client.connected()) {
    Serial.println("Erro na conexão MQTT!");
    configuracoes_mqtt();
  }
}
