import machine
from machine import Pin, Timer, RTC, PWM
import network
from time import sleep
import sys
import esp32
import ubinascii
import urequests
import math
import struct
from umqtt.robust import MQTTClient
from umqtt.simple import MQTTClient
import random
import json
import urequests
from crypt import*
try:
    import usocket as socket
except:
    import socket

pwm_led_board = PWM(Pin(13))
led_board = Pin(13, Pin.OUT)
led_red = Pin(14, Pin.OUT)
led_green = Pin(33, Pin.OUT)
button1 = Pin(32, Pin.IN, Pin.PULL_UP)
button2 = Pin(15, Pin.IN, Pin.PULL_UP)
led_yellow = Pin(27, Pin.OUT)
switchFlag = -1
vx = 0
vy = 0
vz = 0
freq = 0
adjtemp = 0
tempFlag = 0
firstTemp = 0
ifttt_freq = 0

state = 1
data_state = 1
CONFIG = {
     # Configuration details of the MQTT broker
     "MQTT_BROKER": "farmer.cloudmqtt.com",
     "USER": "tegiwjrd",
     "PASSWORD": "8ATTsaL-5FXL",
     "PORT": 14190,
     "TOPIC": "SessionID",
     "CLIENT_ID": "spinner1"
}

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
nets = wlan.scan()
wlan.connect("Snowblind", "victorreallydumb")
while not wlan.isconnected():
    pass

print("Oh Yes! Get connected")
print("Connected to David-SSID")
macaddr = ubinascii.hexlify(wlan.config('mac'), ':').decode()
print("MAC Address: " + macaddr)
print("IP Address: ", wlan.ifconfig()[0])
print('\n')


topic_pub = "Sensor_Data"
client = None

#def onAcknowledge():
#    global data_state
#    global client
#    global state
#    data_state = 1
#
#    print("inside acknowledge")
#    client.set_callback(onMessage)

    

def onMessage(topic, msg):
    global client
    global data_state
    print("Topic: %s, Message: %s" % (topic, msg))
    #client.publish(topic_pub, str(num))
    
    import machine
    global vx
    global vy
    global vz
    global freq
    global adjtemp
    global ifttt_freq
        
    i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(23), freq=400000)
    i2c.scan()
    accel_address = 83
    temp_address = 72
    config_reg = 3
    bw_rate = 44
    data_format = 49
    OFSX = 30
    OFSY = 31
    OFSZ = 32
    power_ctl = 45
    int_enable = 46
        
    #listen()

    if(data_state == 1):

        xData0 = i2c.readfrom_mem(accel_address, 50, 1)
        xData1 = i2c.readfrom_mem(accel_address, 51, 1)
        
        xAccl = ((xData1[0] & 0x03) * 256) + xData0[0]
        if xAccl > 511:
            xAccl -= 1024
            
        yData0 = i2c.readfrom_mem(accel_address, 52, 1)
        yData1 = i2c.readfrom_mem(accel_address, 53, 1)
            
        yAccl = ((yData1[0] & 0x03) * 256) + yData0[0]
        if yAccl > 511:
            yAccl -= 1024
            
        zData0 = i2c.readfrom_mem(accel_address, 54, 1)
        zData1 = i2c.readfrom_mem(accel_address, 55, 1)
            
        zAccl = ((zData1[0] & 0x03) * 256) + zData0[0]
        if zAccl > 511:
            zAccl -= 1024
                
        tempData0 = i2c.readfrom_mem(temp_address, 1, 1)
        tempData1 = i2c.readfrom_mem(temp_address, 0, 1)
            
        value = (tempData1[0] << 8) | tempData0[0]
        temp = (value & 0xfff) / 16.0
        #temp = (value & 0xfff) / 16.0
        if value & 0x1000:
            temp -= 256.0
            
        adjtemp = temp / 10
        print("temp : %f" %adjtemp)
            
        adjX = xAccl * (1 / 488)
        print("Acceleration in X : %f" %adjX)
        adjY = yAccl * (1 / 488)
        print("Acceleration in Y : %f" %adjY)
        adjZ = zAccl * (1 / 488)
        print("Acceleration in Z : %f" %adjZ)
        
#         if adjX == 0.0:
#             adjX = adjX + 0.01
#         if adjY == 0.0:
#             adjY = adjY + 0.01
#         if (adjZ - 1.0) == 0.0:
#             print("asdfasdfasdf" + str(adjZ))
#             adjZ = 1.01
        
        #payload = str(adjX) + "," + str(adjY) + "," + str(adjZ) + "," + str(adjtemp)
        #print(payload)
        
        #sensor_dict = {'x': str(adjX), 'y': str(adjY), 'z': str(adjZ), 'temp': str(adjtemp)}
        sensor_x = str(abs(adjX))[0:4]
        sensor_y = str(abs(adjY))[0:4]
        sensor_z = str(abs(adjZ))[0:4]
        sensor_temp = str(abs(adjtemp))[0:4]
        
        if (len(sensor_x) == 3):
            sensor_x = sensor_x + "0"
        if (len(sensor_y) == 3):
            sensor_y = sensor_y + "0"
        if (len(sensor_z) == 3):
            sensor_z = sensor_z + "0"
        if (len(sensor_temp) == 3):
            sensor_temp = sensor_temp + "0"
        
            
        sensor_dict = sensor_x + sensor_y + sensor_z + sensor_temp
        #sensor_dict = sensor_dict.encode()
        #sensor_dict = 'b"' + sensor_dict + '"'
        #sensor_dict = 1234123412341234
        #sensor_dict = eval(sensor_dict)
        #print(sensor_dict)
       #str_sensor_dict = str(sensor_dict)
        #with open('data_file.json', 'w') as payload:
            #payload = payload.write()
        payload = json.dumps(sensor_dict)
        #payload = json.dump(sensor_dict)
        payload = payload.encode() #payload in bytes
        payload = payload[1:]
        payload = payload[:-1]
        #print(payload)
        #print(type(payload))
        c = CryptAes(msg)
        
        #IFTTT
        if (ifttt_freq % 5) == 0:
            stuff = {}
            stuff['value1'] = sensor_x + "|||" + sensor_y + "|||" + sensor_z + "|||" + sensor_temp
            stuff['value2'] = c.nodeid
            stuff['value3'] = msg
        
            r = urequests.request("POST", "http://maker.ifttt.com/trigger/spinner_1/with/key/dOFBmA1yBeomD91xv2tZye", json=stuff, headers={"Content-Type": "application/json"})
            print(r.text)        
        
        c.encrypt(payload)
        signed_hmac = c.sign_hmac(msg)
        pl = c.send_mqtt(signed_hmac)
        
        
        client.publish(topic_pub, pl)
        data_state = 2
        ifttt_freq += 1
        #client.set_callback(onAcknowledge)
    elif(data_state == 2):
        #print("data_state is two")
        data_state = 1
    #print("Topic: %s, Message: %s" % (topic, msg))

    
def listen():
    global client
    global state
    #Create an instance of MQTTClient 
    client = MQTTClient(CONFIG['CLIENT_ID'], CONFIG['MQTT_BROKER'], user=CONFIG['USER'], password=CONFIG['PASSWORD'], port=CONFIG['PORT'])
    # Attach call back handler to be called on receiving messages
    client.set_callback(onMessage)
    client.connect()
    client.subscribe(CONFIG['TOPIC'])
    client.subscribe('Acknowledgement')

    print("ESP8266 is Connected to %s and subscribed to %s topic" % (CONFIG['MQTT_BROKER'], CONFIG['TOPIC']))
    while(1):
        client.wait_msg()


def button1Pressed(pin):
    
    press1 = pin.value()
    sleep(0.2)
    press2 = pin.value()
    
    if press1 and not press2:
        pass
    elif not press1 and press2:
        global led_board
        global pwm_led_board
        
        pwm_led_board.deinit()
        led_board.on()
        import machine
        i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(23), freq=400000)
        i2c.scan()
        
        if i2c.scan() != 0:
            print("accelerometer initialized\n")
        else:
            print("error, couldn't find devices\n")
        
        accel_address = 83
        temp_address = 72
        config_reg = 3
        bw_rate = 44
        data_format = 49
        OFSX = 30
        OFSY = 31
        OFSZ = 32
        power_ctl = 45
        int_enable = 46
        
        i2c.writeto_mem(temp_address, config_reg, b'\x80') # set 16bit high res for temperature
        i2c.writeto_mem(accel_address, bw_rate, b'\x0d') # set 800 hz output data rate
        i2c.writeto_mem(accel_address, data_format, b'\x08') # set full resolution and +/- 2g
        
        
        i2c.writeto_mem(accel_address, OFSZ, b'\x40') # set offset of Z axis to 1g
        
        print("accelerometer calibrated\n")
        
        print("temperature sensor initialized\n")
        
        i2c.writeto_mem(accel_address, int_enable, b'\x80') # enable interrupt
        i2c.writeto_mem(accel_address, power_ctl, b'\x08') # start measuring
        
        
        global switchFlag
        if switchFlag == 1 or -1:
            switchFlag = 0
        
        sleep(0.5)
        
def button2Pressed(pin):
    
    press1 = pin.value()
    sleep(0.2)
    press2 = pin.value()
    
    if press1 and not press2:
        pass
    elif not press1 and press2:
        global switchFlag
        global led_board
        global pwm_led_board
        global led_board
        global pwm_led_board
        global freq

        led_board.off()
        pwm_led_board.init()
        freq = 10
        pwm_led_board.freq(freq)
        pwm_led_board.duty(512)
        
        if switchFlag == 0 or switchFlag == -1:                
            switchFlag = 1
            listen()
            
def pwm_temperature(timer):
    if switchFlag != 1:
        pass
    else:
        
        global tempFlag
        global first_temp
        
        if tempFlag == 0:
            first_temp = adjtemp
            #print("firstTemp: ", first_temp)
            tempFlag = 1
        elif tempFlag == 1:
            #print("firstTemp: ", first_temp)
            pass
        
        freq = 10 + ((math.trunc(adjtemp - first_temp)) * 5)
        pwm_led_board.freq(freq)
        
button1.irq(trigger = Pin.IRQ_FALLING, handler = button1Pressed)
button2.irq(trigger = Pin.IRQ_FALLING, handler = button2Pressed)
#softTimer = Timer(-1)
#softTimer.init(period = 50, mode = Timer.PERIODIC, callback = velocity)
hardTimer = Timer(0)
hardTimer.init(period = 200, mode = Timer.PERIODIC, callback = pwm_temperature)
