import time

from my_client import My_Client
import re
import sys

filepath = 'asdo.log'
client = None
gps = []


def parse_line(line):
    # Line 5661644: 2021/07/01 20:40:51.635024081 10.181.40.24 AUD Navigation Navigation.cpp@357: Publishing NavigationMessage( 52.6228, 1.41293, 393, HIGH, 62.824 )
    m = re.search('.*([\d]{2}:[\d]{2}:[\d]{2}).*$', line)
    time_str = None
    if m:
        time_str = m.group(1)
        ftr = [3600, 60, 1]
        time_secs = sum([a * b for a, b in zip(ftr, map(int, time_str.split(':')))])
        print(time_secs)

    m = re.search('^.*\((.*)\).*$', line)
    nav_msg =  None
    if m:
        nav_msg = m.group(1)
    return (time_secs, nav_msg)

def nav_msg_to_msg(data):
    lat, lng, odo, conf, speed = data.split(',')
    conf_enum = {'ERROR':0, 'LOW':1, 'MEDIUM':2, 'HIGH':3}
    conf = conf_enum.get(conf.strip())
    nav_msg = '{"latitude":' + lat + ',"longitude":' + str(lng) + ',"odometer":' + str(odo) + ',"confidence":' + str(conf) + ',"odospeed":' + str(speed) + '}'
    return str(nav_msg)

def parse_log_file(client, log_file):
    global gps
    with open(log_file) as fp:
        cnt = 0
        line = fp.readline()
        while line:
            cnt += 1
            if "Publishing NavigationMessage" in line:
                update = 1
                delay = 0.2

                # Always print error, every 1:update lines
                if ("HIGH" not in line) or (not cnt % update):
                    print("{}: {}".format(cnt, line.strip()))
                    (time_secs, nav_data) = parse_line(line)

                    if time_secs:
                        client.publish('/timestamp', '{"seconds":' + str(time_secs) + '}')

                    if nav_data:
                        g = nav_data.split(',')[:2]
                        gps.append(g)
                        nav_msg = nav_msg_to_msg(nav_data)
                        client.publish('/consist/out/navigation', nav_msg)
                        time.sleep(delay)
                cnt += 1
            line = fp.readline()


def main(argv):
    main_client = My_Client()
    main_client.connect('localhost')
    parse_log_file(main_client, 'asdo.log')


if __name__ == "__main__":
    main(sys.argv[1:])
