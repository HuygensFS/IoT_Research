#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include "Adafruit_CCS811.h"

WiFiClient espClient;
PubSubClient client(espClient);

const char* ssid = "IS3L";
const char* password = "ErasmusKustar";
//const char* mqttServer = "postman.cloudmqtt.com";
const char* mqttServer = "10.231.234.184";//"193.136.205.56";//"193.136.230.233";
const int mqttPort = 1883;
//const int mqttPort = 14877;
const char* mqttUser = "pkmtmkxo";
const char* mqttPassword = "cY9ZBQTUMmKs";

Adafruit_CCS811 ccs;

float valores_temp[10];
float valores_TVOC[10];
float valores_CO2[10];

float CO2 = 0;
float TVOC = 0;
float temp = 0;
float CO2_anterior = 0;
float TVOC_anterior = 0;
float temp_anterior = 0;

StaticJsonDocument<300> JSONbuffer;
JsonObject JSONencoder = JSONbuffer.to<JsonObject>();

int ledPinG = 13;
int ledPinV = 14;

int cont = 1;

void setup() {
  Serial.begin(115200);
  pinMode (ledPinG, OUTPUT);
  pinMode (ledPinV, OUTPUT);

  if (!ccs.begin()) {
    Serial.println("Failed to start sensor! Please check your wiring.");
    while (1);
  }

  //calibrate temperature sensor
  while (!ccs.available());
  float temp = ccs.calculateTemperature();
  ccs.setTempOffset(temp - 25.0);
  
  configuracoes_rede();
  configuracoes_mqtt();
}

void loop() {
  digitalWrite (ledPinV, LOW);
  digitalWrite (ledPinG, HIGH);

  static uint32_t beat = 0;
  static uint32_t beat_ant = 0;
  if (millis() - beat > 1000 * cont) {
    cont++;
    Serial.print("Valor do contador: ");
    Serial.println(cont);
    Serial.print("Valor do tempo: ");
    Serial.println(millis() - beat);
    digitalWrite (ledPinV, LOW);
    digitalWrite (ledPinG, HIGH);

    if (millis() - beat < 5*60000) {
      if (ccs.available()) {
        temp = ccs.calculateTemperature();
        if (!ccs.readData()) {
          TVOC = ccs.getTVOC();
          CO2 = ccs.geteCO2();
          
          Serial.print("CO2: ");
          Serial.print(CO2);
          Serial.print("ppm, TVOC: ");
          Serial.print(TVOC);
          Serial.print("ppb   Temp:");
          Serial.println(temp);
        }
        else {
          Serial.println("ERROR!");
        }
      }
    }
    else {
      cont = 1;
      digitalWrite (ledPinV, HIGH);
      digitalWrite (ledPinG, HIGH);

      Serial.println("Enviando dados!");
      char result[8];

      erro_rede();
      Serial.print("TVOC: ");
      Serial.println(CO2);
      Serial.print("TVOC anterior: ");
      Serial.println(TVOC_anterior);

      /*if (temp != temp_anterior) {
        Serial.println("Enviando temperatura!");
        dtostrf(temp, 6, 2, result);
        client.publish("esp/temperature", result);
        //client.subscribe("esp/temperature");
        Serial.print("Enviei temperatura");
        temp_anterior = temp;
      }

      if (TVOC != TVOC_anterior) {
        dtostrf(TVOC, 6, 2, result);
        client.publish("esp/tvoc", result);
        //client.subscribe("esp/tvoc");
        Serial.print(" e TVOC. | ");
        TVOC_anterior = TVOC;
      }

      if (CO2 != CO2_anterior) {
        dtostrf(CO2, 6, 2, result);
        client.publish("esp/co2", result);
        //client.subscribe("esp/co2");
        Serial.print(", CO2");
        CO2_anterior = CO2;
      }*/

      if (temp != temp_anterior || TVOC != TVOC_anterior || CO2 != CO2_anterior) {
        JSONencoder["device"] = "ESP32";
        JSONencoder["sensorType"] = "CO2 Sensor";
        JSONencoder["temperature"] = temp;
        JSONencoder["TVOC"] = TVOC;
        JSONencoder["CO2"] = CO2;
        char JSONmessageBuffer[100];
        serializeJson(JSONencoder,JSONmessageBuffer,sizeof(JSONmessageBuffer));
        client.publish("esp/co2", JSONmessageBuffer);
        //dtostrf(TVOC, 6, 2, result);
        //client.publish("esp/tvoc", result);
        //client.subscribe("esp/tvoc");
        Serial.print(" e TVOC. | ");
        TVOC_anterior = TVOC;
        CO2_anterior = CO2;
        temp_anterior = temp;
      }
      
      beat = millis();
      if (beat_ant > beat)
        beat = 0;
      else
        beat_ant = beat;
    }
  }
  //Serial.print("MQTT connection state: ");
  //Serial.println(client.state());
}

void configuracoes_rede() {
  digitalWrite (ledPinV, HIGH);
  digitalWrite (ledPinG, LOW);
  static uint32_t beat = 0;
  static uint32_t beat_ant = 0;
  WiFi.disconnect();
  WiFi.begin(ssid,password);
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
    if (client.connect("gas")) {
      //if (client.connect("movement", mqttUser, mqttPassword )) {
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
  client.publish("esp/connect", "gas");
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
//
//float calculos(float valores[]) {
//
//  Serial.println("Passei por aqui14!");
//  float media = 0;
//  for (int i = 0; i < 10; i++) {
//    media += valores[i];
//  }
//  media = media / 10;
//
//  float tabela_aux[10];
//  for (int i = 0; i < 10; i++) {
//    tabela_aux[i] = (valores[i] - media) * (valores[i] - media);
//  }
//
//  float tabela_soma = 0;
//  for (int i = 0; i < 10; i++) {
//    tabela_soma += tabela_aux[i];
//  }
//  float desvio_padrao = sqrt(tabela_soma / 10);
//
//  float media_final = 0;
//  int total = 0;
//  for (int i = 0; i < 10; i++) {
//    if ((media - desvio_padrao <= valores[i]) && (media + desvio_padrao >= valores[i])) {
//      media_final += valores[i];
//      total++;
//    }
//  }
//  return media_final / total;
//}
