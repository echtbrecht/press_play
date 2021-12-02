from paho.mqtt import client as mqtt_client
import logging


class Controller:
    """This object simulates a controller"""

    def on_connect(self):
        logging.info(f"{self.identifier} is connected to broker")

    def __init__(self, identifier='FF:FF:FF:FF', broker_address='localhost'):
        self.identifier = identifier
        self.mqtt_client = mqtt_client.Client(identifier)
        self.mqtt_client.username_pw_set('username', 'password')
        self.mqtt_client.connect(broker_address,1883)

    def send_a_button_press(self, button_name=1):
        # Build a topic so that Telegraf will pick this up
        topic = f"controllers/{self.identifier}/input"
        # Make a message so that
        msg = f"controllers,id={self.identifier} button_name={button_name}"
        self.mqtt_client.publish(topic, msg)



def run():
    logging.INFO('Script started!')
    first_controller = Controller()
    first_controller.send_a_button_press()

if __name__ == '__main__':
    run()
