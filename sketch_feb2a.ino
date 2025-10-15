#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASS";
const char* mqtt_server = "RPI_IP"; // Raspberry Pi IP

WiFiClient espClient;
PubSubClient client(espClient);

#define BUZZER 5
#define RELAY 18

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (int i=0; i<length; i++) msg += (char)payload[i];
  if (msg == "ALERT=1") {
    digitalWrite(BUZZER, HIGH);
    digitalWrite(RELAY, HIGH);
    delay(3000);
    digitalWrite(BUZZER, LOW);
    digitalWrite(RELAY, LOW);
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP32Alert")) {
      client.subscribe("/alert");
    } else delay(2000);
  }
}

void setup() {
  pinMode(BUZZER, OUTPUT);
  pinMode(RELAY, OUTPUT);
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
}
