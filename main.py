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
setpoint = 500;
user_intensity = 0xFF0000


def hex_to_string(hex):
    hexdict = {
        0x00001A: 10,
        0x000033: 20,
        0x00004D: 30,
        0x000066: 40,
        0x000080: 50,
        0x000099: 60,
        0x0000B3: 70,
        0x0000CC: 80,
        0x0000E6: 90,
        0x0000F: 100,
        0xFF0000: 0,
    }
    return hexdict.get(hex, "Invalid Number")


def string_to_hex(number):
    if 10 > number > -1:
        return 0x00001A
    if 20 > number > 10:
        return 0x000033
    if 30 > number > 20:
        return 0x00004D
    if 40 > number > 30:
        return 0x000066
    if 50 > number > 40:
        return 0x000080
    if 60 > number > 50:
        return 0x000099
    if 70 > number > 60:
        return 0x0000B3
    if 80 > number > 70:
        return 0x0000CC
    if 90 > number > 80:
        return 0x0000E6
    if 101 > number > 90:
        return 0x0000FF


def sub_cb(topic, msg):
    m_decode = str(msg.decode("utf-8", "ignore"))
    retrieved_message = ujson.loads(m_decode)
    global user_intensity
    global setpoint
    user_intensity = string_to_hex(retrieved_message["intensity"])
    setpoint=retrieved_message["setpoint"]



for net in nets:
    if net.ssid == 'ID':
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
    light = lt.light()
    averageLight = ((light[0] + light[1]) / 2)
    pycom.rgbled(user_intensity)

    #TODO: set points



    #if 300 > averageLight > 0:
    #    pycom.rgbled(0xFF7300)  # Orange
    #    utime.sleep(1)
    #if 600 > averageLight > 300:
    #    pycom.rgbled(0x00FFF2)  # light blue
    #    utime.sleep(1)
    #if 1200 > averageLight > 600:
    #    pycom.rgbled(0xFFFF00)  # Yellow
    #    utime.sleep(1)
    #if 5000 > averageLight > 1200:
    #    pycom.rgbled(0x00FF00)  # Green
    #    utime.sleep(1)
    #if 15000 > averageLight > 5000:
    #    pycom.rgbled(0x0000FF)  # Blue
    #    utime.sleep(1)
    #if averageLight > 15000:
    #    pycom.rgbled(0xFF0000)  # Red
    #    utime.sleep(1)
    utime.sleep(1)
    if wlan.isconnected():
        try:
            datadict = {
                "light_level": averageLight,
                "time_stamp":  rtc.now(),
                "setpoint": setpoint,
                "light_intensity": hex_to_string(user_intensity)
            }
            msg = ujson.dumps(datadict)
            client.publish(topic="test", msg=msg)
            client.check_msg()
        except OSError as err:
            print("Error!" + str(err), utime.time())

