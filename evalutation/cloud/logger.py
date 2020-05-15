import os
import paho.mqtt.client as mqtt
import json
from datetime import datetime
from urllib.parse import urlparse
import time

url_str = os.environ.get('CLOUDMQTT_URL')
url = urlparse(url_str)

def on_connect(client, userdata, rc):
    client.subscribe("$SYS/#")

file_name = 'logger_times2.csv'
myFile = open(file_name, 'w+')
myFile.write("LoggerBefore,DeviceTime,Light,Setpoint,Intensity,MessageCount,LoggerAfter\n")
def on_message(client, userdata, message):
    myFile.write("%.9f," % time.time()) # Before sending
    
    data_object = json.loads(message.payload)
    t = data_object['time_stamp']
    t_convert = datetime(year=t[0], month=t[1], day=t[2], hour=t[3], minute=t[4], second=t[5], microsecond=t[6])
    
    timestamp = t_convert.timestamp()
    light_value = data_object['light_level']
    setpoint_value = data_object['setpoint']
    intensity_value = data_object['light_intensity']
    message_count = data_object['message_counter']

    myFile.write("%d," % light_value)
    myFile.write("%d," % setpoint_value)
    myFile.write("%d," % intensity_value)
    myFile.write("%d," % message_count)
    myFile.write("%.9f\n" % time.time()) # After sending

    

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


client.username_pw_set(url.username, url.password)
client.connect(url.hostname, url.port)

client.subscribe(topic="device/1")

client.loop_forever()