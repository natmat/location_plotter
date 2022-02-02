import threading

import paho.mqtt.client as mqtt
import json
import sys

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/consist/out/navigation")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    s = (msg.payload).decode("utf-8")
    try:
        gps = json.loads(s)
    except Exception as e:
        print("Error: " + repr(e))

    # print(gps)
    try:
        lat = gps['latitude']
        lng = gps['longitude']
        My_Mqtt.on_message_cbf(lat, lng)
    except Exception as e:
        print("Error: " + repr(e))


class My_Mqtt:
    on_message_cbf = None

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message

        # client.connect("10.183.200.11", 1883)
        self.client.connect("localhost", 1883)

    def run(self, cbf):
        My_Mqtt.on_message_cbf = cbf
        self.client.loop_start()


def main(argv):
    mqtt = My_Mqtt()
    # mqtt.run()


if __name__ == "__main__":
    main(sys.argv[1:])
