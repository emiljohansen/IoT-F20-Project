from network import WLAN
from pysense import Pysense
from LTR329ALS01 import LTR329ALS01
from machine import Pin, ADC, UART, RTC
import utime
import urequests
import pycom
import ujson
from mqtt import MQTTClient



url = 'http://192.168.1.101:5000/temp'

pycom.heartbeat(False)

wlan = WLAN(mode=WLAN.STA)
uart = UART(0, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

py = Pysense()
lt = LTR329ALS01(py)

utime.sleep(5)
nets = wlan.scan()
messageCounter = 0
errorCounter = 0

for net in nets:
    if net.ssid == 'SSID':
        wlan.connect(net.ssid, auth=(net.sec, 'PASSWORD'))
        print("Connected to wifi")
        client = MQTTClient("device_id", "io.adafruit.com", user="your_username", password="your_api_key", port=1883)
        client.set_callback(sub_cb)
        client.connect()
        client.subscribe(topic="youraccount/feeds/lights")

        while not wlan.isconnected():
            pass
        break
while True:
    messageCounter += 1
    timestamp = "%.9f" % utime.time()
    light = lt.light()
    pycom.rgbled(0xFF0000)
    utime.sleep(1)
    if wlan.isconnected():
        try:
            client.publish(topic="youraccount/feeds/lights", msg="Light Level: " + light)
        except OSError as err:
            print("Error!" + str(err), utime.time())
            errorCounter += 1
        r.close()
    else:
        errorCounter += 1

def sub_cb(topic, msg):
   print(msg)


