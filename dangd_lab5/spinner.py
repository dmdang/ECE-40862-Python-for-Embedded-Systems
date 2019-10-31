import machine
from machine import Pin, Timer, RTC, PWM
from time import sleep
import sys
import ubinascii
import math

pwm_led_board = PWM(Pin(13))
led_board = Pin(13, Pin.OUT)
led_red = Pin(14, Pin.OUT)
led_green = Pin(33, Pin.OUT)
led_yellow = Pin(27, Pin.OUT)
button1 = Pin(32, Pin.IN, Pin.PULL_UP)
button2 = Pin(15, Pin.IN, Pin.PULL_UP)
switchFlag = -1
vx = 0
vy = 0
vz = 0
freq = 0
adjtemp = 0
tempFlag = 0
firstTemp = 0

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
        
#--------------------------DEBUG--------------------------
        
#        xData0 = i2c.readfrom_mem(accel_address, 50, 1)
#        xData1 = i2c.readfrom_mem(accel_address, 51, 1)
#        
#        xAccl = ((xData1[0] & 0x03) * 256) + xData0[0]
#        if xAccl > 511:
#            xAccl -= 1024
#        
#        yData0 = i2c.readfrom_mem(accel_address, 52, 1)
#        yData1 = i2c.readfrom_mem(accel_address, 53, 1)
#        
#        yAccl = ((yData1[0] & 0x03) * 256) + yData0[0]
#        if yAccl > 511:
#            yAccl -= 1024
#        
#        zData0 = i2c.readfrom_mem(accel_address, 54, 1)
#        zData1 = i2c.readfrom_mem(accel_address, 55, 1)
#        
#        zAccl = ((zData1[0] & 0x03) * 256) + zData0[0]
#        if zAccl > 511:
#            zAccl -= 1024
#            
#        tempData0 = i2c.readfrom_mem(temp_address, 1, 1)
#        tempData1 = i2c.readfrom_mem(temp_address, 0, 1)
#        
#        value = (tempData1[0] << 8) | tempData0[0]
#        temp = (value & 0xfff) / 16.0
#        #temp = (value & 0xfff) / 16.0
#        if value & 0x1000:
#            temp -= 256.0
#        
#        adjtemp = temp / 10
#        print("temp : %f" %adjtemp)
#        
#        adjX = xAccl * (9.8 / 488)
#        print("Acceleration in X : %f" %adjX)
#        adjY = yAccl * (9.8 / 488)
#        print("Acceleration in Y : %f" %adjY)
#        adjZ = zAccl * (9.8 / 488)
#        print("Acceleration in Z : %f" %adjZ)
        
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
            
def velocity(timer):
    
    if switchFlag != 1:
        pass
    else:
        import machine
        global vx
        global vy
        global vz
        global freq
        global adjtemp
        
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
        
        adjX = xAccl * (9.8 / 488)
        #print("Acceleration in X : %f" %adjX)
        adjY = yAccl * (9.8 / 488)
        #print("Acceleration in Y : %f" %adjY)
        adjZ = zAccl * (9.8 / 488)
        #print("Acceleration in Z : %f" %adjZ)
        
        if adjX <= 0.1 and adjX >= -0.4:
            vx = 0.0
        elif adjY >= 0.0 and adjY <= 0.5:
            vy = 0.0
        elif adjZ >= 9.5 and adjZ <= 10.0:
            vz = 0.0
        else:
            vx += adjX * .05 
            vy += adjY * .05
            vz += adjZ * .05
            
        print("vx : ", vx)
        print("vy : ", vy)
        print("vz : ", vz)
        
        if vx > 10 or vy > 10 or vz > 10 or vx < -10 or vy < -10 or vz < -10:
            led_red.on()
        else:
            led_red.off()
        
        pitch = 100 * (math.atan(float(adjX) / (math.sqrt(math.pow(adjY,2) + math.pow(adjZ,2)))))
        roll = 100 * (math.atan(float(adjY) / (math.sqrt(math.pow(adjX,2) + math.pow(adjZ,2)))))
        theta = 100 * (math.atan(math.sqrt(math.pow(adjX,2) + math.pow(adjY,2)) / float(adjZ)))
        
        print("pitch : ", pitch)
        print("roll : ", roll)
        print("theta : ", theta)
        
        if pitch > 30 or roll > 30 or theta > 30 or pitch < -30 or roll < -30 or theta < -30:
            led_yellow.on()
        else:
            led_yellow.off()
        
        if vx == 0.0 and vy == 0.0 and vz == 0.0:
            led_green.on()
        else:
            led_green.off()
    
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
softTimer = Timer(-1)
softTimer.init(period = 50, mode = Timer.PERIODIC, callback = velocity)
hardTimer = Timer(0)
hardTimer.init(period = 200, mode = Timer.PERIODIC, callback = pwm_temperature)