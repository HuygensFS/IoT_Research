
#include <PubSubClient.h>
#include <WiFi.h>
#include "esp_system.h"

WiFiClient espClient;
PubSubClient client(espClient);

//
const char* ssid = "IS3L";
const char* password = "ErasmusKustar";
//const char* mqttServer = "postman.cloudmqtt.com";
const char* mqttServer = "10.231.234.184";
const int mqttPort = 1883;
//const int mqttPort = 14877;
const char* mqttUser = "pkmtmkxo";
const char* mqttPassword = "cY9ZBQTUMmKs";

int relayPin_0 = 22;
int relayPin_1 = 23;
//int local_s_0 = 14;
int local_s_1 = 15;
int val = 0;
int val_ant = 1;
int Switch_0 = 0;
int Switch_1 = 0;
int last_state_0 = 0;
int last_state_1 = 0;
int p_0 = 0;
int p_1 = 0;
//WatchDog
/*hw_timer_t *timer = NULL;
const int wdtTimeout = 30*60000;

void IRAM_ATTR resetModule() {
  ets_printf("reboot\n");
  configuracoes_rede();
  configuracoes_mqtt();
  client.subscribe("esp/relay",1);
  //esp_restart();
}*/
//--------

void setup() {
  Serial.begin(115200);
  pinMode(relayPin_0, OUTPUT);
  pinMode(relayPin_1, OUTPUT);
  //pinMode(local_s_0, INPUT);
  pinMode(local_s_1, INPUT);
  configuracoes_rede();
  configuracoes_mqtt();

  //Config WatchDog
  /*timer = timerBegin(0, 80, true);                  
  timerAttachInterrupt(timer, &resetModule, true);  
  timerAlarmWrite(timer, wdtTimeout * 1000, false); 
  timerAlarmEnable(timer);*/

  digitalWrite(relayPin_0, HIGH);
  digitalWrite(relayPin_1, HIGH);
  Switch_0 = 1;
  Switch_1 = 1;
  
  client.subscribe("esp/relay",1);
}

void callback(char* topic, byte* payload, unsigned int length) {

  //timerWrite(timer, 0);//reset timer (feed watchdog)
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
 
  /*Serial.print("Message:");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }*/
  if((char)payload[0] == '0' && Switch_0 == 0)
  {
    Serial.println("Relay 0 On");
    digitalWrite(relayPin_0, HIGH);
    Switch_0 = 1;
    client.publish("esp/relay_state_0", "0");
  }
  else if((char)payload[0] == '0' && Switch_0 == 1)
  {
    Serial.println("Relay 0 Off");
    digitalWrite(relayPin_0, LOW);
    Switch_0 = 0;
    client.publish("esp/relay_state_0", "1");
  }
  else if((char)payload[0] == '1'&& Switch_1 == 0)
  {
    Serial.println("Relay 1 On");
    digitalWrite(relayPin_1, HIGH);
    Switch_1 = 1;
    client.publish("esp/relay_state_1", "0");
  }
  else if((char)payload[0] == '1' && Switch_1 == 1)
  {
    Serial.println("Relay 1 Off");
    digitalWrite(relayPin_1, LOW);
    Switch_1 = 0;
    client.publish("esp/relay_state_1", "1");
  }
  else if((char)payload[0] == '2')
  {
    Serial.println("Watching the Dog!");
  }
 
}

void loop() {
  //p_0 = digitalRead(local_s_0);
  p_1 = digitalRead(local_s_1);
  /*if(p_0 != last_state_0 && Switch_0 == 0)
  {
    Serial.println("Relay 0 On");
    digitalWrite(relayPin_0, HIGH);
    Switch_0 = 1;
    if(client.connected())
    {
      client.publish("esp/relay_state_0", "0");
    }
  }
  else if(p_0 != last_state_0 && Switch_0 == 1)
  {
    Serial.println("Relay 0 Off");
    digitalWrite(relayPin_0, LOW);
    Switch_0 = 0;
    if(client.connected())
    {
      client.publish("esp/relay_state_0", "1");
    }
  }*/

  if(p_1 != last_state_1 && Switch_1 == 0)
  {
    Serial.println("Relay 1 On");
    digitalWrite(relayPin_1, HIGH);
    digitalWrite(relayPin_0, HIGH);//REMOVE
    Switch_1 = 1;
    if(client.connected())
    {
      client.publish("esp/relay_state_1", "0");
    }
  }
  else if(p_1 != last_state_1 && Switch_1 == 1)
  {
    Serial.println("Relay 1 Off");
    digitalWrite(relayPin_1, LOW);
    digitalWrite(relayPin_0, LOW);//REMOVE
    Switch_1 = 0;
    if(client.connected())
    {
      client.publish("esp/relay_state_1", "1");
    }
  }
  
  last_state_0 = p_0;
  last_state_1 = p_1;
  client.loop();
}

void configuracoes_rede() {
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
}

void configuracoes_mqtt() {
  static uint32_t beat = 0;
  static uint32_t beat_ant = 0;

  client.setServer(mqttServer, mqttPort);
  
  int contador = 0;
  while (!client.connected()) {
    Serial.println("Connecting to MQTT…");
    String clientId = "ESP32Client-";
    //clientId += String(random(0xffff), HEX);
    if (client.connect("relay")) {
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
  client.publish("esp/connect", "relay");
  client.setCallback(callback);
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
