import random
import sys
import time

from paho.mqtt import client as mqtt


class mqtt_wrapper:
    broker = 'localhost'
    port = 1883
    topic = "gps"

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect

    @classmethod
    def on_connect(cls, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
            sys.exit(1)

    def connect(self):
        self.client.connect(mqtt_wrapper.broker, mqtt_wrapper.port)

    def publish(self, msg):
        msg_count = 0
        result = self.client.publish(mqtt_wrapper.topic, msg)

        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{mqtt_wrapper.topic}`")
        else:
            print(f"Failed to send message to topic {mqtt_wrapper.topic}")
        msg_count += 1

    def disconnect(self):
        self.client.disconnect()


def main():
    client = mqtt_wrapper()
    client.connect()
    for i in range(1, 11):
        client.publish("Message: " + str(i))
        time.sleep(1)
    client.disconnect()


if __name__ == "__main__":
    main()
