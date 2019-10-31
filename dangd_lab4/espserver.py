import machine
from machine import Pin, Timer
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

# Global variables
led_red = Pin(14, Pin.OUT)
led_green = Pin(33, Pin.OUT)
button1 = Pin(32, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(15, Pin.IN, Pin.PULL_DOWN)

temp = esp32.raw_temperature()  # measure temperature sensor data
hall = esp32.hall_sensor()# measure hall sensor data
red_led_state = 'ON' if led_red.value() == 1 else 'OFF'  # string, check state of red led, ON or OFF
green_led_state = 'ON' if led_green.value() == 1 else 'OFF' # string, check state of red led, ON or OFF
button1_state = 'ON' if button1.value() == 1 else 'OFF'
button2_state = 'ON' if button2.value() == 1 else 'OFF'

def web_page():
    """Function to build the HTML webpage which should be displayed
    in client (web browser on PC or phone) when the client sends a request
    the ESP32 server.
    
    The server should send necessary header information to the client
    (YOU HAVE TO FIND OUT WHAT HEADER YOUR SERVER NEEDS TO SEND)
    and then only send the HTML webpage to the client.
    
    Global variables:
    TEMP, HALL, RED_LED_STATE, GREEN_LED_STAT
    """
    temp = esp32.raw_temperature()  
    hall = esp32.hall_sensor()
    red_led_state = 'ON' if led_red.value() == 1 else 'OFF'
    green_led_state = 'ON' if led_green.value() == 1 else 'OFF'
    button1_state = 'ON' if button1.value() == 1 else 'OFF'
    button2_state = 'ON' if button2.value() == 1 else 'OFF'
    
    html_webpage = """<!DOCTYPE HTML><html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <style>
    html {
     font-family: Arial;
     display: inline-block;
     margin: 0px auto;
     text-align: center;
    }
    h2 { font-size: 3.0rem; }
    p { font-size: 3.0rem; }
    .units { font-size: 1.5rem; }
    .sensor-labels{
      font-size: 1.5rem;
      vertical-align:middle;
      padding-bottom: 15px;
    }
    .button {
        display: inline-block; background-color: #e7bd3b; border: none; 
        border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none;
        font-size: 30px; margin: 2px; cursor: pointer;
    }
    .button2 {
        background-color: #4286f4;
    }
    </style>
    </head>
    <body>
    <h2>ESP32 WEB Server</h2>
    <p>
    <i class="fas fa-thermometer-half" style="color:#059e8a;"></i> 
    <span class="sensor-labels">Temperature</span> 
    <span>"""+str(temp)+"""</span>
    <sup class="units">&deg;F</sup>
    </p>
    <p>
    <i class="fas fa-bolt" style="color:#00add6;"></i>
    <span class="sensor-labels">Hall</span>
    <span>"""+str(hall)+"""</span>
    <sup class="units">V</sup>
    </p>
    <p>
    RED LED Current State: <strong>""" + red_led_state + """</strong>
    </p>
    <p>
    <a href="/?red_led=on"><button class="button">RED ON</button></a>
    </p>
    <p><a href="/?red_led=off"><button class="button button2">RED OFF</button></a>
    </p>
    <p>
    GREEN LED Current State: <strong>""" + green_led_state + """</strong>
    </p>
    <p>
    <a href="/?green_led=on"><button class="button">GREEN ON</button></a>
    </p>
    <p><a href="/?green_led=off"><button class="button button2">GREEN OFF</button></a>
    </p>
    <p>
    SWITCH1 Current State: <strong>""" + button1_state + """</strong>
    </p>
    <p>
    <a href="/?button1=on"></a>
    </p>
    <p>
    <a href="/?button1=off"></a>
    </p>
    <p>
    SWITCH2 Current State: <strong>""" + button2_state + """</strong>
    </p>
    <p>
    <a href="/?button2=on"></a>
    </p>
    <p>
    <a href="/?button2=off"></a>
    </p>
    </body>
    </html>"""
    return html_webpage

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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    
    client, addr = s.accept()
    
    request = client.recv(1024)
    request = str(request)
    red_led_on = request.find('/?red_led=on')
    red_led_off = request.find('/?red_led=off')
    green_led_on = request.find('/?green_led=on')
    green_led_off = request.find('/?green_led=off')
    button1_on = request.find('/?button1=on')
    button1_off = request.find('/?button1=off')
    button2_on = request.find('/?button2=on')
    button2_off = request.find('/?button2=off')
    
    if red_led_on == 6:
        led_red.value(1)
        
    if red_led_off == 6:
        led_red.value(0)
        
    if green_led_on == 6:
        led_green.value(1)
        
    if green_led_off == 6:
        led_green.value(0)
    
    if button1_on == 6:
        button1.value(1)
        
    if button1_off == 6:
        button1.value(0)
        
    if button2_on == 6:
        button2.value(1)
        
    if button2_off == 6:
        button2.value(0)
    
    
    response = web_page()
    client.send('HTTP/1.1 200 OK\n')
    client.send('Content-Type: text/html\n')
    client.send('Connection: close\n\n')
    client.sendall(response)
    client.close()
        
        
    