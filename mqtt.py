import threading
import time

import paho.mqtt.client as mqtt_client
import json
import sys


class My_Mqtt:
    timestamp = 0

    def __init__(self, broker='localhost'):
        self.client = mqtt_client.Client()
        self.client.on_connect = self.connect_cbf
        self.client.on_message = self.message_cbf

        # block until connected
        connected = False
        while not connected:
            try:
                self.client.connect(broker)
                connected = True
            except Exception as e:
                print("Error: " + repr(e))
                time.sleep(1)

    def connect_cbf(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to Broker: " + mqtt_client.connack_string(rc))
        else:
            print("Failed to connect, return code %d\n", rc)
            sys.exit(1)

        self.client.subscribe('/consist/out/navigation')
        # self.client.subscribe('/timestamp')

    # The callback for when a PUBLISH message is received from the server.
    def message_cbf(self, client, userdata, msg):
        print("message_cbf")
        s = (msg.payload).decode("utf-8")

        if msg.topic == '/timestamp':
            try:
                ts = json.loads(s)
            except Exception as e:
                print("Error: " + repr(e))

            try:
                seconds = ts.get('seconds')
                print(seconds)
                delta  = seconds - My_Mqtt.timestamp
                print(delta)
                My_Mqtt.timestamp = seconds
            except Exception as e:
                print("Error: " + repr(e))

            return

        try:
            gps = json.loads(s)
        except Exception as e:
            print("Error: " + repr(e))

        # print(gps)
        try:
            latitude = gps.get('latitude')
            longitude = gps.get('longitude')
            odometer = gps.get('ododmeter')
            confidence = gps.get('confidence')
            speed = gps.get('odospeed')
            My_Mqtt.on_message_cbf(latitude, longitude, confidence)
        except Exception as e:
            print("Error: " + repr(e))

    def run(self, cbf):
        self.connect_cbf = cbf
        self.client.loop_forever()

def test_cbf(client, userdata, msg):
    print("test_cbf(): " + msg)


def main(argv):
    mqtt = My_Mqtt('localhost')
    mqtt.run(test_cbf)


if __name__ == "__main__":
    main(sys.argv[1:])
