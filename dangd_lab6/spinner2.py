import esp32
from machine import RTC
from machine import Timer
from time import sleep
from machine import Pin, I2C
import machine
from time import sleep
import math
from machine import PWM
import network
import struct
from umqtt.robust import MQTTClient
from umqtt.simple import MQTTClient
import random
import json
from crypt import*
import urequests


led_red = Pin(15, Pin.OUT)
pwmled = PWM(Pin(27))
pwmled.freq(10)
pwmled.duty(512)
ifttt_count = 4

freq = 10
tempstart = 0
start = 1

CONFIG = {
     # Configuration details of the MQTT broker
     "MQTT_BROKER": "farmer.cloudmqtt.com",
     "USER": "tegiwjrd",
     "PASSWORD": "8ATTsaL-5FXL",
     "PORT": 14190,
     "TOPIC": "Sensor_Data",
     "CLIENT_ID": "spinner2"
}

gen = 0
topic_pub = "SessionID"
client = None
num = 0
WIFI_SSID = "Snowblind"
WIFI_PW = "victorreallydumb"


print("Oh Yes! Get connected")
wlan = network.WLAN(network.STA_IF)

wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PW)

sleep(5)

print("Connected to " + WIFI_SSID)

ipaddr = wlan.ifconfig()[0]
print("IP Address: " + ipaddr)

def onMessage(topic, msg):
    global num
    global client
    global gen

    gen = 0
    print("Message: %s" % (msg))
    #msg = msg + '"' + "}"
    #msg = str(msg)
    #msg = msg[2:]
    #msg = msg[:-1]
    #print(type(msg))
    #data = json.loads(msg)
    data = eval(msg)
    #print(data)
    c = CryptAes(num)
    data = c.verify_hmac(data,num)
    if(data != "Failed Authentication"):
        print(data)
        print("Success")
        ledcontrol(data)
    else:
        print("Failed")
        gen = 1
 
def listen():
    global num
    global client
    global gen
    #Create an instance of MQTTClient 
    client = MQTTClient(CONFIG['CLIENT_ID'], CONFIG['MQTT_BROKER'], user=CONFIG['USER'], password=CONFIG['PASSWORD'], port=CONFIG['PORT'])
    # Attach call back handler to be called on receiving messages
    client.set_callback(onMessage)
    client.connect()
    client.subscribe(CONFIG['TOPIC'])
    print("ESP32 is Connected to %s and subscribed to %s topic" % (CONFIG['MQTT_BROKER'], CONFIG['TOPIC']))
    gen = 1
    while(1):
        client.check_msg()

def randnum(test):
    global gen
    global client
    global num
    
    if(gen == 1):
        num = random.randint(1,10000)
        client.publish(topic_pub, str(num))

        
def ledcontrol(data):
    global led_red 
    global pwmled
    global tempstart
    global start
    global freq
    global state
    global gen
    global ifttt_count
    
    data = eval(data)
    #print(type(data))

    #print(abs(float(data['decrypt_data'][0:4])))
    #print(abs(float(data['decrypt_data'][4:8])))
    #print(abs(float(data['decrypt_data'][8:12])))
    #print(abs(float(data['decrypt_data'][12:16])))
    if(abs(float(data['decrypt_data'][0:4])) > 0.3):
        led_red.value(1)
    elif(abs(float(data['decrypt_data'][4:8])) > 0.3):
        led_red.value(1)
    elif(abs(float(data['decrypt_data'][8:12])) > 1.3):    
        led_red.value(1)
    else:
        led_red.value(0)
    
    tempprint = float(data['decrypt_data'][12:16])
    if(start == 1):
        tempstart = tempprint
        start = 2
    freq = 10 + (math.trunc(tempprint - tempstart) * 5)
    pwmled.freq(freq)
    print("Temperature : %f" %tempprint)
    client.publish('Acknowledgement', 'Successful Decryption')
    print('Ack')
    
    ifttt_count += 1
    if(ifttt_count >= 5):
        nodeID = "1919181817171616"
        report = {}
        report["value1"] = str(float(data['decrypt_data'][0:4])) + "|||" + str(float(data['decrypt_data'][4:8])) + "|||" + str(float(data['decrypt_data'][8:12]))
        report["value2"] = str(float(data['decrypt_data'][12:16])) + "|||" + nodeID
        report["value3"] = str(num)
        #report["value4"] = temp
        r = urequests.request("POST", "http://maker.ifttt.com/trigger/spinner_2/with/key/c1GVtb7TnmhNsSCERilY6_", json=report, headers={"Content-Type": "application/json"})
        #r.close()
        print("IFTTT")
        print(r.text)
        ifttt_count = 0
    gen = 1

        
    

timer1 = Timer(0)
timer1.init(period=3000, mode=Timer.PERIODIC, callback=randnum)
listen()



