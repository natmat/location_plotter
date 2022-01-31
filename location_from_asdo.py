import mqtt_client
import re
import sys

filepath = 'asdo.log'
client = None

def parse_line(line):
    # Line 5661644: 2021/07/01 20:40:51.635024081 10.181.40.24 AUD Navigation Navigation.cpp@357: Publishing NavigationMessage( 52.6228, 1.41293, 393, HIGH, 62.824 )
    m = re.search('^.*\((.*)\).*$', line)
    if m:
        found = m.group(1)
    gps = found.split(',')[:2]
    return (gps)


def pub_line(line):
    (lat, lng) = parse_line(line)
    client.


def open_log_file(log_file, client):
    with open(log_file) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            if "Publishing NavigationMessage" in line:
                print("Line {}: {}".format(cnt, line.strip()))
                pub_line(line)

            line = fp.readline()
            cnt += 1


def main(argv):
    global client
    client = mqtt_client()
    client
    client.loop_start(client)

    open_log_file('asdo.log')


if __name__ == "__main__":
    main(sys.argv[1:])
