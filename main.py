from mqtt import MQTTClient
from network import WLAN
from pysense import Pysense
from LTR329ALS01 import LTR329ALS01
from machine import Pin, ADC, UART, RTC
import utime
import urequests
import pycom
import ujson
import mqtt_cred as cred

pycom.heartbeat(False)

wlan = WLAN(mode=WLAN.STA)
uart = UART(0, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

import machine
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")

py = Pysense()
lt = LTR329ALS01(py)

utime.sleep(5)
nets = wlan.scan()
messageCounter = 0
errorCounter = 0


def sub_cb(topic, msg):
    retrived_message = ujson.loads(msg)
    print(retrived_message)


for net in nets:
    if net.ssid == 'SSID':
        wlan.connect(net.ssid, auth=(net.sec, 'PASSWORD'))
        print("Connected to wifi")
        utime.sleep(5)
        client = MQTTClient(cred.USER, cred.BROKER, user=cred.USER, password=cred.PASSWORD, port=cred.PORT)
        client.set_callback(sub_cb)
        client.connect()
        client.subscribe(topic="pycom")
        #client.subscribe(topic="youraccount/feeds/lights")

        while not wlan.isconnected():
            pass
        break
while True:
    messageCounter += 1
    timestamp = "%.9f" % utime.time()
    light = lt.light()
    averageLight = ((light[0] + light[1]) / 2)
    if 300 > averageLight > 0:
        pycom.rgbled(0xFF7300)  # Orange
        utime.sleep(1)
    if 600 > averageLight > 300:
        pycom.rgbled(0x00FFF2)  # light blue
        utime.sleep(1)
    if 1200 > averageLight > 600:
        pycom.rgbled(0xFFFF00)  # Yellow
        utime.sleep(1)
    if 5000 > averageLight > 1200:
        pycom.rgbled(0x00FF00)  # Green
        utime.sleep(1)
    if 15000 > averageLight > 5000:
        pycom.rgbled(0x0000FF)  # Blue
        utime.sleep(1)
    if averageLight > 15000:
        pycom.rgbled(0xFF0000)  # Red
        utime.sleep(1)
    if wlan.isconnected():
        try:
            datadict = {
                "light_level": averageLight,
                "time_stamp":  rtc.now(),
                "setpoint": "default",
                "light_intensity": "easy"
            }
            msg = ujson.dumps(datadict)
            client.publish(topic="test", msg=msg)
            client.check_msg()
        except OSError as err:
            print("Error!" + str(err), utime.time())

