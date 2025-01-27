from machine import Pin, PWM
class Motor:
    def __init__(self):
        self.m1Dir = Pin(7 , Pin.OUT) # set pin left wheel
        self.pwm1 = PWM(Pin(6))
        self.pwm1.freq(1000)
        self.pwm1.duty_u16(0)
    def off(self):
        self.pwm1.duty_u16(0)
    def Forward(self):
        self.m1Dir.value(0) # forward = 0 reverse = 1 motor 1
        self.pwm1.duty_u16(int(65535*100/100)) # speed range 0-100 motor 1
    def Reverse(self):
        self.m1Dir.value(1)
        self.pwm1.duty_u16(int(65535*30/100))
motor= Motor()
motor.Forward()
