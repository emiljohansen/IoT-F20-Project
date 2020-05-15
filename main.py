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

SSID = 'SSID'
PASSWORD = 'PASSWORD'

import machine
rtc = machine.RTC()

py = Pysense()
lt = LTR329ALS01(py)

utime.sleep(5)
nets = wlan.scan()
messageCounter = 0
errorCounter = 0

intensityNumber = 0
intensity = 0xFF0000

setpoint = 0
user_intensity = 0xFF0000
count = 0
list_lights = []
userDefinedPreset = False
userDefinedIntensity = False
dutyCycle = 3

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


def number_to_hex(number):
    if 11 > number > 0:
        return 0x00001A
    if 21 > number > 11:
        return 0x000033
    if 31 > number > 21:
        return 0x00004D
    if 41 > number > 31:
        return 0x000066
    if 51 > number > 41:
        return 0x000080
    if 61 > number > 51:
        return 0x000099
    if 71 > number > 61:
        return 0x0000B3
    if 81 > number > 71:
        return 0x0000CC
    if 91 > number > 81:
        return 0x0000E6
    if 101 > number > 91:
        return 0x0000FF
    if number > 101:
        return 0x000000
    if number < 1:
        return 0x000000


def sub_cb(topic, msg):
    m_decode = str(msg.decode("utf-8", "ignore"))
    t_decode = str(topic.decode("utf-8", "ignore"))
    retrieved_message = ujson.loads(m_decode)
    print(t_decode + " , " + m_decode)
    if t_decode == "device/1/setpoint":
        global setpoint
        global userDefinedPreset
        global userDefinedIntensity
        setpoint = retrieved_message["setpoint_value"]
        userDefinedPreset = True
        userDefinedIntensity = False

    if t_decode == "device/1/intensity":
        global user_intensity
        global userDefinedPreset
        global userDefinedIntensity
        global intensityNumber
        user_intensity = number_to_hex(retrieved_message["intensity_value"])
        intensityNumber = retrieved_message["intensity_value"]
        userDefinedIntensity = True
        userDefinedPreset = False


def decrease_intensity(number):
    global intensity
    global intensityNumber
    intensityNumber -= number
    if intensityNumber < 0:
        intensityNumber = 0
    intensity = number_to_hex(intensityNumber)
    pycom.rgbled(intensity)


def increase_intensity(number):
    global intensityNumber
    global intensity
    intensityNumber += number
    if intensityNumber > 100:
        intensityNumber = 100
    intensity = number_to_hex(intensityNumber)
    pycom.rgbled(intensity)

def median():
    list_lights.sort()
    length = len(list_lights)
    if length % 2 == 0:
        initial_median = list_lights[length//2]
        proceding_median = list_lights[length//2 - 1]
        median = (initial_median + proceding_median) / 2
    else:
        median = list_lights[length // 2]
    return median

for net in nets:
    if net.ssid == SSID:
        wlan.connect(net.ssid, auth=(net.sec, PASSWORD))
        print("Connected to wifi")
        utime.sleep(5)
        rtc.ntp_sync("time.windows.com")
        client = MQTTClient(cred.USER, cred.BROKER, user=cred.USER, password=cred.PASSWORD, port=cred.PORT)
        client.set_callback(sub_cb)
        client.connect()
        client.subscribe(topic="device/1/intensity")
        client.subscribe(topic="device/1/setpoint")

        while not wlan.isconnected():
            pass
        break
while True:
    light = lt.light()
    averageLight = light[0]
    if userDefinedIntensity == True:
        pycom.rgbled(user_intensity)
        utime.sleep(1)
    if userDefinedPreset == True:
        if count <= dutyCycle:
            list_lights.append(averageLight)
            count += 1
        else:
            median_value = median()
            list_lights.clear()
            count = 0
            if median_value < setpoint:
                increase_intensity(10)
            if median_value > setpoint:
                decrease_intensity(10)
    #utime.sleep(1)
    messageCounter += 1
    if wlan.isconnected():
        try:
            datadict = {
                "light_level": averageLight,
                "time_stamp":  rtc.now(),
                "setpoint": setpoint,
                "light_intensity": intensityNumber,
                "message_counter": messageCounter
            }
            msg = ujson.dumps(datadict)
            client.publish(topic="device/1", msg=msg)
            client.check_msg()
        except OSError as err:
            print("Error!" + str(err), utime.time())