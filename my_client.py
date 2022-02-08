import random
import sys
import threading
import time

import paho.mqtt.client as mqtt_client
from pip._vendor.distlib.compat import raw_input


def yes_or_no(question):
    while "the answer is invalid":
        reply = str(raw_input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False


class My_Client:
    broker = 'localhost'

    def __init__(self):
        self.is_connected = False
        self.client = mqtt_client.Client()
        self.client.on_connect = self.connect_cbf
        self.client.on_disconnect = self.disconnect_cbf

    def connect_cbf(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to Broker: " + mqtt_client.connack_string(rc))
        else:
            print("Failed to connect, return code %d\n", rc)
            sys.exit(1)
        self.is_connected = True

    def disconnect_cbf(self, client, userdata, rc):
        print("disconnected")
        if rc != 0:
            print("Unexpected disconnection.")

        # self.th.stop()

        if yes_or_no("Reconnect? "):
            self.client.reconnect()

    def connect(self, broker='localhost'):
        My_Client.broker = broker
        connected = False
        while not connected:
            self.client.connect(My_Client.broker)
            connected = True

    def publish(self, topic, msg):
        result = self.client.publish(topic, msg)
        if result[0] is False:
            print(f"Failed to send message to topic {topic}")

    def disconnect(self):
        self.client.disconnect()


def publish_timetamp(in_client):
    while not in_client.is_connected:
        time.sleep(1)

    for i in range(1, 6):
        topic = '/timestamp'
        msg = str(i)
        print(topic, msg)
        in_client.client.publish(topic, msg)
        time.sleep(1.0)
    in_client.client.loop_stop()
    in_client.disconnect()

def run():
    client = My_Client()
    client.connect()

    th = threading.Thread(target=publish_timetamp, args=(client,))
    th.start()

    client.client.loop_forever()


if __name__ == "__main__":
    run()
