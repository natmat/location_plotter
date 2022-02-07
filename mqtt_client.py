import random
import sys
import time

from paho.mqtt import client as mqtt
from pip._vendor.distlib.compat import raw_input


def yes_or_no(question):
    while "the answer is invalid":
        reply = str(raw_input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False

class mqtt_client:
    broker = 'localhost'
    port = 1883
    topic = "/consist/out/navigation"

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    @classmethod
    def on_connect(cls, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
            sys.exit(1)

    def on_disconnect(self, client, userdata, rc):
        print("disconnected")
        if rc != 0:
            print("Unexpected disconnection.")

        if yes_or_no("Reconnect? "):
            client.reconnect()

    def connect(self, broker='localhost'):
        mqtt_client,broker = broker
        self.client.connect(mqtt_client.broker, mqtt_client.port)

    def publish(self, msg):
        result = self.client.publish(mqtt_client.topic, msg)
        if result[0] is False:
            print(f"Failed to send message to topic {mqtt_client.topic}")

    def disconnect(self):
        self.client.disconnect()


def run():
    client = mqtt_client()
    client.connect()
    for i in range(1, 5):
        client.publish("Message: " + str(i))
        time.sleep(0.1)

    client.disconnect()


if __name__ == "__main__":
    run()
