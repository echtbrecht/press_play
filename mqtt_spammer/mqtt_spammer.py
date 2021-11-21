import random
import threading
from paho.mqtt import client as mqtt_client

broker = 'localhost'
port = 1883
topic = "mqtt_spammer"


class spammer(threading.Thread):
    client_id = ''

    def __init__(self):
        threading.Thread.__init__(self)
        self.client_id = f'python-mqtt-{random.randint(0, 100000000)}'
        self.client = connect_mqtt(self.client_id)

    def run(self):
        publish(self.client, self.client_id)


def connect_mqtt(client_id):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set("test", "testje")
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, client_id):
    msg_count = 0
    while msg_count < 1000:
        msg = f"votes,ID={client_id} vote={msg_count}"
        result = client.publish(topic, msg, qos=1)
        # result: [0, 1]
        status = result[0]
        if status != 0:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1


def run():
    number_of_threads = 1000
    i = 0
    while i < number_of_threads:
        thread = spammer()
        thread.start()
        i += 1


if __name__ == '__main__':
    run()
