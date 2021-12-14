# MQTT tree & line protocol


## MQTT interface

All our systems will talk will talk fluently MQTT. MQTT is based on a 'publish & subscribe' mechanism.

### ESP32 - the controller
The controller needs to send data to our database & needs to receive commands from higher systems.


| Topic                           | Value           | MQTT task         | Comment                                                                                                                                                                                  |
|---------------------------------|-----------------|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| controllers/#macaddress#/input  | #line_protocol# | publish           | All things that need to be stored to the database: button presses, diagnostics, ...                                                                                                  |
| controllers/#macaddress#/output | #json object#   | subscribe         | All things that a *specific* controller needs to do: light up buttons, print text, ...                                                                                               |
| controllers/#macaddress#/im_alive            | #line_protocol# | publish/last will | All things regarding onboarding and offboarding: on first connect an "I'm alive" message can be send, on connection lost, the broker can send a specific "I'm dead" message.|
| controllers/output              | #json object#   | subscribe         | All things that *all* controllers need to do: * Send a diagnostics string (battery level, uptime, connected bssid) *                                                                     |


The input topic and I'm alive topic need to follow the line protocol so that these topics can be stored directly in the influxDB database.

**controllers/#macaddress#/input - line protocol**
The controller can publish on this topic

Example for a button message
```
controllers,id=D8F3A5A646FB button_name=1
```
Example for a diagnostic message
```
diagnostics,id=D8F3A5A646FB,wifi_bssid=D8F3A5A646FB signal_strength=-50,battery_voltage=2.4,uptime=15530
```

Example for an im_alive message
```
im_alive,id=D8F3A5A646FB status=1  #Controller is alive!
im_alive,id=D8F3A5A646FB status=0  #Controller is dead!
```

**controllers/#macaddress#/output - json**

This JSON is to be decided by those who want to control the controllers. Good luck!