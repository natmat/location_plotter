Usage:

1. Input from asdo.log file

In one terminal location_from_asdo.py that parses the asdo.log file and MQTT publishes the Navigation message:
./python3 location_from_asdo.py

In another, run maps.py to dynamically plot the navigation.

To adjust the rate of MQTT publishing, change these globals:
NAV_MSG_SKIP = 10       # Only published 1:NAV_MSG_SKIP messages
NAV_MSG_INTERVAL = 0.1  # Interval (in seconds) between MQTT pubs


