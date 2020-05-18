import paho.mqtt.publish as pub
import os
import random
import json
from datetime import datetime
import time

from urllib.parse import urlparse

url_str = os.environ.get('CLOUDMQTT_URL')
url = urlparse(url_str)
auth_info = { 'username' : url.username, 'password' : url.password}

def pub_data_to_mqtt(topic, message):
    pub.single(topic, payload=message, hostname=url.hostname, port=url.port, auth=auth_info)

valid_setpoints = [0, 1, 2, 3, 4, 5]
valid_intensities = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
file_name = 'command_times.csv'
with open(file_name, 'w+') as myFile:
    myFile.write("Before,After,Value\n")
    while True:
        #value = random.choice(valid_intensities)
        value = random.choice(valid_setpoints)

        myFile.write("%.9f," % time.time()) # Before sending
        pub_data_to_mqtt(topic="device/{id}/setpoint".format(id=1), message=json.dumps({'setpoint_value': value}))
        #pub_data_to_mqtt(topic="device/{id}/intensity".format(id=1), message=json.dumps({'intensity_value': value}))
        myFile.write("%.9f," % time.time())
        myFile.write("%d\n" % value) # After sending

        time.sleep(5)