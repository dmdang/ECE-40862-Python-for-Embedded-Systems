import machine
from machine import Pin, Timer, RTC, TouchPad
import network
from time import sleep
import sys
import esp32
import ntptime
import ubinascii

led_red = Pin(14, Pin.OUT)
led_green = Pin(33, Pin.OUT)
greenTouch = TouchPad(Pin(4))
redTouch = TouchPad(Pin(12))
button1 = Pin(32, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(15, Pin.IN, Pin.PULL_DOWN)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
nets = wlan.scan()
wlan.connect("David", "zyx74082L11")
while not wlan.isconnected():
    pass

if machine.wake_reason() == machine.EXT1_WAKE:
    print("\n")
    print("Woke up due to push button")
    print("\n")
elif machine.wake_reason() == machine.TIMER_WAKE:
    print("\n")
    print("Woke up due to timer")
    print("\n")
elif machine.wake_reason() == machine.TOUCHPAD_WAKE:
    print("\n")
    print("Woke up due to Touchpad")
    print("\n")
    
led_red.on()

print("Oh Yes! Get connected")
print("Connected to David-SSID")
macaddr = ubinascii.hexlify(wlan.config('mac'), ':').decode()
print("MAC Address: " + macaddr)
print("IP Address: ", wlan.ifconfig()[0])
print('\n')

ntptime.settime()


def hardDispTime(timer):
    date = rtc.datetime()
    day = date[2]
    hr = date[4]
    hr = hr - 4
    if hr < 0:
        hr = hr + 24
    
    print("Date: " + "0" + str(date[1]) + "/" + str(day) + "/" + str(date[0]))
    print("Time: " + str(hr) + ":" + str(date[5]) + ":" + str(date[6]) + " HRS")
    print('\n')
    
rtc = RTC()
hardTimer = Timer(0)
hardTimer.init(period = 15000, mode = Timer.PERIODIC, callback = hardDispTime)



# turn on/off green led
def greenTouchSensor(timer):
    if greenTouch.read() < 300:
        led_green.on()
    else:
        led_green.off()

        
#button wakeup
esp32.wake_on_ext1(pins = (button1, button2), level = esp32.WAKEUP_ANY_HIGH)

#touchpad wakeup
redTouch.config(300)
esp32.wake_on_touch(True)
        
#deepsleep
def deepsleep(timer):
    print("I am awake. Going to sleep for 1 minute")
    machine.deepsleep(60000)
    
hardTimer3 = Timer(2)
hardTimer3.init(period = 30000, mode = Timer.PERIODIC, callback = deepsleep)

hardTimer2 = Timer(1)
hardTimer2.init(period = 10, mode = Timer.PERIODIC, callback = greenTouchSensor)

