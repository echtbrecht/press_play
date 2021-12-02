#include <ESP8266WiFi.h>
#include <ArduinoMqttClient.h>

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

void setup()
{
  Serial.begin(9600);
  Serial.println();

  WiFi.begin("Nerdlab", "Nerdlabiseengevoel");

  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  Serial.print("Connected, IP address: ");
  Serial.println(WiFi.localIP());
  
  if (!mqttClient.connect("192.168.0.101", 1883)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());

    while (1);
  }
  
  Serial.println("You're connected to the MQTT broker!");
  
}

void loop() {

  // send message, the Print interface can be used to set the message contents
  mqttClient.beginMessage("controllers/" + WiFi.macAddress() + "/input");
  mqttClient.print("controllers,id=D8F3A5A646FB button_name=1");
  mqttClient.endMessage();
  Serial.println();
  delay(5000);
}