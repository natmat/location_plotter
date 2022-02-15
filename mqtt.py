import threading
from time import sleep

import paho.mqtt.client as mqtt
import json
import sys

def on_connect(client, userdata, flags, rc):
    if rc == mqtt.MQTT_ERR_SUCCESS:
        print("Connected with result code " + str(rc))
        client.subscribe("/consist/out/navigation")
    else:
        print("Bad connection Returned code=", rc)
        client.bad_connection_flag = True
        sys.exit(1)
    print("## CONNECTED ##")


def on_disconnect(client, userdata, rc):
    print("Disconnected with result code " + str(rc))
    if rc != mqtt.MQTT_ERR_SUCCESS:
        print("Unexpected disconnection.")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    s = (msg.payload).decode("utf-8")
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


class My_Mqtt:
    on_message_cbf = None

    def __init__(self, broker='localhost'):
        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect

        # block until connected
        try:
            self.client.connect(broker, 1883)
        except Exception as e:
            print("Error: " + repr(e))
            sys.exit(1)

    def run(self, cbf):
        My_Mqtt.on_message_cbf = cbf
        self.client.loop_start()


def main(argv):
    mqtt = My_Mqtt()
    # mqtt.run()


if __name__ == "__main__":
    main(sys.argv[1:])
