import random
import threading
import logging
from paho.mqtt import client as mqtt_client
from datetime import datetime
from influxdb_client import InfluxDBClient
import pandas

endpoint = 'localhost'
port = 1883

class Spammer(threading.Thread):
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
    client.connect(endpoint, port)
    return client


def publish(client, client_id):
    msg_count = 0
    while msg_count < 100:
        msg = f"controllers,id={client_id} button_name={msg_count}"
        topic = f"controllers/{client_id}/input"
        result = client.publish(topic, msg, qos=0)
        status = result[0]
        if status != 0:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1


def run():

    number_of_threads = 100
    logging.info(f'Script started! Fire up our test controllers. {number_of_threads} "virtual" controllers will be started')
    start_time = datetime.utcnow()
    i = 0
    while i < number_of_threads:
        thread = Spammer()
        thread.start()
        i += 1
    logging.info("All messages are send. Now checking how much of these messages are stored")

    # Set up the influx db client
    influx_url = f"http://{endpoint}:8086"
    logging.info(f"Connecting to {influx_url}")
    client = InfluxDBClient(url=influx_url, token='oursecrettoken')
    query_api = client.query_api()

    time_format ="%Y-%m-%dT%H:%M:%SZ"
    query =f"""from(bucket: "telegraf_data")
  |> range(start: {start_time.strftime(format=time_format)}, stop: {datetime.utcnow().strftime(format=time_format)})
  |> filter(fn: (r) => r["_measurement"] == "controllers")
  |> group()
  |> sort(columns: ["_time"])
  |> keep(columns: ["_value"])
  |> count()
"""
    result = client.query_api().query_data_frame(org="press_play", query=query)
    number_of_records_found = result['_value'].iloc[0]
    number_of_records_expected = 100 * number_of_threads
    logging.info(f"{number_of_records_found} records found, {number_of_records_expected} records expected")
    logging.info(f"{number_of_records_found*100/number_of_records_expected}% received")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
