from machine import Pin, PWM
from utime import sleep
class Motor: #this is for all the motors, Weels, linear actuator and etc.
    def __init__(self , pin, PMW):
        self.m1Dir = Pin(pin , Pin.OUT) # set pins 
        self.pwm1 = PWM(Pin(PMW))
        self.pwm1.freq(1000)
        self.pwm1.duty_u16(0)
    def off(self):
        self.pwm1.duty_u16(0)
    def Forward(self, speed):
        self.m1Dir.value(0) # forward = 0 reverse = 1 motor 1
        self.pwm1.duty_u16(int(65535*speed/100)) # speed range 0-100 motor 1
    def Reverse(self, speed):
        self.m1Dir.value(1)
        self.pwm1.duty_u16(int(65535*speed/100))#
        
class Wheels : 
    def __init__(self):
        self.wheel_right= Motor(7,6)
        self.wheel_left = Motor(4,5)
    def forward (self):
        self.wheel_right.Forward(90)
        self.wheel_left.Forward(90)
    def turn_right (self, level) :
        if level == 0 :
            self.wheel_right.Forward(80)
            self.wheel_left.Forward(100)
        elif level ==1 :
            self.wheel_right.Forward(60)
            self.wheel_left.Reverse(60)
    def turn_left (self,level):
        if level == 0 :
            self.wheel_right.Forward(100)
            self.wheel_left.Forward(80)
        elif level ==1 :
            self.wheel_right.Forward(60)
            self.wheel_left.Reverse(60)
    def off(self):
        self.wheel_right.off()
        self.wheel_left.off()
wheels = Wheels()
sleep(2)
wheels.turn_left(1)
sleep(12)
wheels.off()
