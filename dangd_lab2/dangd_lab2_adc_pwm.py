from machine import Pin, Timer, RTC, ADC, PWM
from time import sleep
import sys
from gc import collect

led_red_pwm, led_green_pwm = PWM(Pin(14)), PWM(Pin(33))
led_red_pwm.deinit()
led_green_pwm.deinit()
year = int(input("Year? "))
month = int(input("Month? "))
day = int(input("Day? "))
weekday = int(input("Weekday? "))
hour = int(input("Hour? "))
minute = int(input("Minute? "))
second = int(input("Second? "))
microsecond = int(input("Microsecond? "))
led_red_pwm.init()
led_green_pwm.init()
#Hardware Timer
def hardDispTime(timer):
        print("Date: " + str(rtc.datetime()[1]) + "." + str(rtc.datetime()[2]) + "." + str(rtc.datetime()[0]))
        print("Time: " + str(rtc.datetime()[4]) + ":" + str(rtc.datetime()[5]) + ":" + str(rtc.datetime()[6]))
        #print(rtc.datetime())

hardTimer = Timer(0)
rtc = RTC()
rtc.datetime((year, month, day, weekday, hour, minute, second, microsecond))
hardTimer.init(period = 30000, mode = Timer.PERIODIC, callback = hardDispTime)

#Software Timer / ADC
switchFlag = -1
def softDispPot(timer):
    print(pot.read())
    if switchFlag == 1:
        #control red led freq
        led_red_pwm, led_green_pwm = PWM(Pin(14)), PWM(Pin(33))
        led_green_pwm.duty(256)
        led_red_pwm.freq(int(pot.read() / 136))
        if pot.read() < 136:
            led_red_pwm.freq(5)

    elif switchFlag == 0:
        led_red_pwm, led_green_pwm = PWM(Pin(14)), PWM(Pin(33))
        led_green_pwm.freq(10)
        led_green_pwm.duty(int(pot.read() / 5))
    
pot = ADC(Pin(32))
softTimer = Timer(-1)
softTimer.init(period = 100, mode = Timer.PERIODIC, callback = softDispPot)

#PWM / button interrupt
led_red_pwm, led_green_pwm = PWM(Pin(14)), PWM(Pin(33))
button = Pin(15, Pin.IN, Pin.PULL_UP)
led_red_pwm.freq(10)
led_red_pwm.duty(256)
led_green_pwm.freq(10)
led_green_pwm.duty(256)

#macaddr = ubinascii.hexlify(wlan.config('mac'), ':').decode()

def buttonPressed(pin):
    
    press1 = pin.value()
    sleep(0.2)
    press2 = pin.value()
    
    if press1 and not press2:
        pass
    elif not press1 and press2:
        global switchFlag
        global led_green_pwm
        global led_red_pwm
        if switchFlag == 0 or switchFlag == -1:                
            switchFlag = 1
        else:
            switchFlag = 0
    
button.irq(trigger = Pin.IRQ_FALLING, handler = buttonPressed)