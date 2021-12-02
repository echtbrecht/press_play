import threading

from paho.mqtt import client as mqtt_client
import logging
import random


class Controller:
    """This object simulates a controller"""

    def on_connect(self):
        logging.info(f"{self.identifier} is connected to broker")

    def __init__(self, identifier='FF:FF:FF:FF', broker_address='localhost'):
        self.identifier = identifier
        self.mqtt_client = mqtt_client.Client(identifier)
        self.mqtt_client.username_pw_set('username', 'password')
        self.mqtt_client.will_set(f"controllers/{self.identifier}/im_alive", f"controllers,id={self.identifier} im_alive=False")
        self.mqtt_client.connect(broker_address, 1883)
        self.mqtt_client.publish(f"controllers/{self.identifier}/im_alive", f"controllers,id={self.identifier} im_alive=True")

    def send_a_button_press(self, button_name=1):
        # Build a topic so that Telegraf will pick this up
        topic = f"controllers/{self.identifier}/input"
        # Make a message so that
        msg = f"controllers,id={self.identifier} button_name={button_name}"
        self.mqtt_client.publish(topic, msg)


class Thread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        mac_address = "02:00:00:%02x:%02x:%02x" % (
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        controller = Controller(mac_address)
        controller.send_a_button_press(random.randint(0, 5))



def run():
    logging.info('Script started!')
    first_controller = Controller()
    first_controller.send_a_button_press()

    number_of_threads = 1000
    i = 0
    while i < number_of_threads:
        thread = Thread()
        thread.start()
        i += 1


if __name__ == '__main__':
    run()
