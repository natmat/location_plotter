import time

from mqtt_client import mqtt_client
import re
import sys

filepath = 'asdo.log'
client = None
gps = []


def get_gps(line):
    # Line 5661644: 2021/07/01 20:40:51.635024081 10.181.40.24 AUD Navigation Navigation.cpp@357: Publishing NavigationMessage( 52.6228, 1.41293, 393, HIGH, 62.824 )
    m = re.search('^.*\((.*)\).*$', line)
    if m:
        found = m.group(1)
    gps = found.split(',')[:2]
    return (gps)


def print_gps(line):
    (lat, lng) = get_gps(line)
    print("(" + lat, lng + ")")


def parse_log_file(client, log_file):
    global gps
    with open(log_file) as fp:
        cnt = 1
        line = fp.readline()
        while line:
            if "Publishing NavigationMessage" in line:
                if not cnt % 100:
                    print("{}: {}".format(cnt, line.strip()))
                    gps.append(get_gps(line))
                    client.publish(line)
                    time.sleep(0.1)
                cnt += 1
            line = fp.readline()


def main(argv):
    client = mqtt_client()
    client.connect()
    parse_log_file(client, 'asdo.log')


if __name__ == "__main__":
    main(sys.argv[1:])
