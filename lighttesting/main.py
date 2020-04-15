from pysense import Pysense
from LTR329ALS01 import LTR329ALS01
import utime
import pycom

py = Pysense()
lt = LTR329ALS01(py)
pycom.heartbeat(False)

while True:
    light = lt.light()
    averageLight = ((light[0] + light[1]) / 2)
    if 300 > averageLight > 0:
        pycom.rgbled(0xFF7300)#Orange
    if 600 > averageLight > 300:
        pycom.rgbled(0x00FFF2)#light blue
        utime.sleep(1)
    if 1200 > averageLight > 600:
        pycom.rgbled(0xFFFF00)#Yellow
        utime.sleep(1)
    if 5000 > averageLight > 1200:
        pycom.rgbled(0x00FF00)#Green
        utime.sleep(1)
    if 15000 > averageLight > 5000:
        pycom.rgbled(0x0000FF)#Blue
        utime.sleep(1)
    if averageLight > 15000:
        pycom.rgbled(0xFF0000)#Red
        utime.sleep(1)
    print(light)
    utime.sleep(1)
