import time

from mqtt_client import mqtt_client
import re
import sys

filepath = 'asdo.log'
client = None
gps = []


def parse_line(line):
    # Line 5661644: 2021/07/01 20:40:51.635024081 10.181.40.24 AUD Navigation Navigation.cpp@357: Publishing NavigationMessage( 52.6228, 1.41293, 393, HIGH, 62.824 )
    m = re.search('^.*\((.*)\).*$', line)
    nav_msg =  None
    if m:
        nav_msg = m.group(1)
    return nav_msg

def nav_msg_to_msg(data):
    lat, lng, odo, conf, speed = data.split(',')
    conf_enum = {'ERROR':0, 'LOW':1, 'MEDIUM':2, 'HIGH':3}
    conf = conf_enum.get(conf.strip())
    nav_msg = '{"latitude":' + lat + ',"longitude":' + str(lng) + ',"odometer":' + str(odo) + ',"confidence":' + str(conf) + ',"odospeed":' + str(speed) + '}'
    return str(nav_msg)

def parse_log_file(client, log_file):
    global gps
    with open(log_file) as fp:
        cnt = 1
        line = fp.readline()
        while line:
            if "Publishing NavigationMessage" in line:
                # Update every 100th NavMsg, wait delay [ms] between publish
                if "HIGH" in line:
                    cnt += 1
                    line = fp.readline()
                    continue

                update = 1
                delay = 0.1

                if not cnt % update:
                    print("{}: {}".format(cnt, line.strip()))
                    data = parse_line(line)
                    if data:
                        g = data.split(',')[:2]
                        gps.append(g)
                        nav_msg = nav_msg_to_msg(data)
                        client.publish(nav_msg)
                        time.sleep(delay)
                cnt += 1
            line = fp.readline()


def main(argv):
    client = mqtt_client()
    client.connect()
    parse_log_file(client, 'asdo.log')


if __name__ == "__main__":
    main(sys.argv[1:])
