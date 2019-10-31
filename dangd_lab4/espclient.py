import machine
from machine import Pin, Timer, RTC
import network
from time import sleep
import sys
import esp32
import ubinascii
import urequests
try:
    import usocket as socket
except:
    import socket


led_red = Pin(14, Pin.OUT)
led_green = Pin(33, Pin.OUT)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
nets = wlan.scan()
wlan.connect("David", "zyx74082L11")
while not wlan.isconnected():
    pass

print("Oh Yes! Get connected")
print("Connected to David-SSID")
macaddr = ubinascii.hexlify(wlan.config('mac'), ':').decode()
print("MAC Address: " + macaddr)
print("IP Address: ", wlan.ifconfig()[0])
print('\n')

def http_get(url):
    import usocket
    _, _, host, path = url.split('/', 3)
    addr = usocket.getaddrinfo(host, 80)[0][-1]
    s = usocket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    response = urequests.get('http://jsonplaceholder.typicode.com/albums/1')
    parsed = response.json()
    s.close()
    
def hardDispTime(timer):
    t = esp32.raw_temperature()
    h = esp32.hall_sensor()
    print("temperature (°F): " + str(t))
    print("hall sensor: " + str(h))
    
    base_url = 'https://api.thingspeak.com/update'
    API_key = '?api_key=R1N8YAFNXLY6MMWM'
    fieldanddata = "&field1="+str(t)+"&field2="+str(h)
    url = base_url + API_key + fieldanddata
    http_get(url)

    
hardTimer = Timer(0)
hardTimer.init(period = 10000, mode = Timer.PERIODIC, callback = hardDispTime)