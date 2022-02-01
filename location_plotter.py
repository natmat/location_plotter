import threading

import paho.mqtt.client as mqtt
import json
import folium
import random
import sys
import time
from threading import Thread, Lock

mutex = Lock()

class Gps:
    def __int__(self, lat=51.6, lng=0.0):
        self.lat = lat
        self.lng = lng

    def set_speed(self, s):
        self.speed = s


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/gps")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic + " " + str(msg.payload))
    # print("msg: " + msg.payload.decode("utf-8"))
    s = (msg.payload).decode("utf-8")
    try:
        gps = json.loads(s)
    except Exception as e:
        print("Error: " + repr(e))
        return

    # print(gps)
    try:
        lat = gps['latitude']
        lng = gps['longitude']
    except Exception as e:
        print(e)

    mutex.acquire()
    try:
        Map.plot_gps(lat, lng)
    finally:
        mutex.release()


class Map:
    file = 'map.html'
    mapper = None
    circle_colour = 0xFFF0F0

    def __init__(self, lat=52.205276, lng=0.119167):
        # Cambridge: lat=52.205276, lng=0.119167)
        mapper = folium.Map(prefer_canvas=True, zoom_start=13, location=(lat, lng))

    @classmethod
    def new_folium_map(cls, lat, lng):
        cls.mapper = folium.Map(prefer_canvas=True, zoom_start=13, location=(lat, lng))
        cls.circle_colour = 0xFFF0F0

        # Add the refresh interval to the file
        with open(cls.file, "r") as f:
            contents = f.readlines()
        contents.insert(4, '\t<meta http-equiv="refresh" content="5">\n')
        with open(cls.file, "w") as f:
            contents = "".join(contents)
            f.write(contents)

    @classmethod
    def plot_random_circles(cls, n):
        for i in range(n):
            lat = random.uniform(51,53)
            lng = random.uniform(-2, 0)
            folium.Circle((lat, lng), radius=50, color='blue').add_to(cls.mapper)

    @classmethod
    def plot_gps(cls, lat, lng):
        print("Plot: " + str(lat) + str(lng))
        if cls.mapper is None:
            cls.new_folium_map(lat, lng)

        # Test with random circles
        # cls.plot_random_circles(n)

        cls.circle_colour -= 0x2020
        col = "'#" + str(hex(cls.circle_colour)[2:]) + "'"
        print(col)
        # folium.Circle((lat, lng), radius=50, color=col, fill=True).add_to(cls.mapper)
        folium.Circle((lat, lng), radius=50, color='#FF0000', fill=True).add_to(cls.mapper)

    @classmethod
    def save(cls):
        mutex.acquire()
        try:
            cls.mapper.save(cls.file)
        except Exception as e:
            print("Error: " + repr(e))
        finally:
            mutex.release()
        cls.mapper = None

def timer_save():
    print("Save map: " + time.ctime())
    Map.save()
    threading.Timer(5, timer_save).start()

def main(argv):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Start print thread
    Map()
    timer_save()

    # client.connect("10.183.200.11", 1883)
    client.connect("localhost", 1883)
    client.loop_forever()


if __name__ == "__main__":
    main(sys.argv[1:])

# mosquitto_pub.exe -t "/consist/out/navigation" -m '{"confidence":0,"latitude":1.1,"longitude":2.2,"odometer":3.3,"odospeed":4.4","speed":5.5"}'

# lng=1
# while : ; do
# lng=$((lng+1)) ; echo $lng
# ./mosquitto_pub.exe -t "/consist/out/navigation" -m '{"confidence":0,"latitude":51.5,"longitude":0.0'${lng}',"odometer":3.3,"odospeed":4.4,"speed":5.5}'
# sleep 1
# done
