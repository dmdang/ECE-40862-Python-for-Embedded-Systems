from machine import Pin
from time import sleep
import sys

led_red = Pin(14, Pin.OUT)
led_green = Pin(32, Pin.OUT)
redButton = Pin(15, Pin.IN, Pin.PULL_UP)
greenButton = Pin(33, Pin.IN, Pin.PULL_UP)
redButtonCount = 0
greenButtonCount = 0
greenOnFlag = 0
redOnFlag = 0

while True:
               
    press1, press3 = redButton.value(), greenButton.value()
    sleep(0.05)
    press2, press4 = redButton.value(), greenButton.value()
    
    if press3 and not press4:
        led_green.on()
        greenOnFlag = 1
        if redOnFlag == 1:
            led_green.off()
            led_red.off()
    elif not press3 and press4:
        led_green.off()
        greenButtonCount += 1
        greenOnFlag = 0
    
    if press1 and not press2:
        led_red.on()
        redOnFlag = 1
        if greenOnFlag == 1:
            led_red.off()
            led_green.off()
    elif not press1 and press2:
        led_red.off()
        redButtonCount += 1
        redOnFlag = 0
        
    if redButtonCount == 10:
        
        currentVal = greenButton.value()
        active = 0
        while active < 20:
            if  greenButton.value() != currentVal:
                active = 50
                led_green.off()
                led_red.off()
                print("You have successfully implemented LAB1 DEMO!!!")
                sys.exit()
            else:
                active = 0
                sleep(0.1)
                led_red.off()
                led_green.on()
                sleep(0.1)
                led_green.off()
                led_red.on()
            sleep(0.02)
            
    if greenButtonCount == 10:
        
        currentVal = redButton.value()
        active = 0
        while active < 20:
            if  redButton.value() != currentVal:
                active = 50
                led_green.off()
                led_red.off()
                print("You have successfully implemented LAB1 DEMO!!!")
                sys.exit()
            else:
                active = 0
                sleep(0.1)
                led_green.off()
                led_red.on()
                sleep(0.1)
                led_red.off()
                led_green.on()
            sleep(0.02)
                
