from time import sleep
from machine import Pin, PWM


class Motor:
    def __init__(self, dir_pin, pwm_pin, freq=1000):
        #"""Generic Motor class for controlling all types of motors."""
        self.dir = Pin(dir_pin, Pin.OUT)  # Direction control
        self.pwm = PWM(Pin(pwm_pin))  # PWM speed control
        self.pwm.freq(freq)  # Set PWM frequency
        self.pwm.duty_u16(0)  # Initialize speed to 0

    def set_speed(self, speed):
        #"""Set motor speed (0-100%)."""
        self.pwm.duty_u16(int(65535 * speed / 100))

    def set_direction(self, direction):
        #"""Set motor direction (0 = forward, 1 = reverse)."""
        self.dir.value(direction)

    def stop(self):
        #"""Stop the motor."""
        self.pwm.duty_u16(0)


class Wheel:
    def __init__(self, left_pins, right_pins):
        #"""Wheel class for two-wheel robot movement."""
        self.left_motor = Motor(*left_pins)  # Left wheel motor
        self.right_motor = Motor(*right_pins)  # Right wheel motor

    def forward(self, speed=90):
        #"""Move both wheels forward."""
        self.left_motor.set_direction(0)
        self.right_motor.set_direction(0)
        self.left_motor.set_speed(speed)
        self.right_motor.set_speed(speed)

    def reverse(self, speed=90):
        #"""Move both wheels backward."""
        self.left_motor.set_direction(1)
        self.right_motor.set_direction(1)
        self.left_motor.set_speed(speed)
        self.right_motor.set_speed(speed)

    def turn_left(self, speed=90):
        #"""Turn left (slow down left wheel, keep right wheel moving)."""
        self.left_motor.set_direction(0)  
        self.right_motor.set_direction(0)  
        self.left_motor.set_speed(speed-10)  # Reduce left wheel speed
        self.right_motor.set_speed(speed+10)

    def turn_right(self, speed=90):
        #"""Turn right (slow down right wheel, keep left wheel moving)."""
        self.left_motor.set_direction(0)
        self.right_motor.set_direction(0)
        self.left_motor.set_speed(speed+10)
        self.right_motor.set_speed(speed-10)  # Reduce right wheel speed

    def rotate_left(self, speed=60):
        #"""Rotate left in place (left wheel backward, right wheel forward)."""
        self.left_motor.set_direction(1)
        self.right_motor.set_direction(0)
        self.left_motor.set_speed(speed)
        self.right_motor.set_speed(speed)

    def rotate_right(self, speed=60):
        #"""Rotate right in place (left wheel forward, right wheel backward)."""
        self.left_motor.set_direction(0)
        self.right_motor.set_direction(1)
        self.left_motor.set_speed(speed)
        self.right_motor.set_speed(speed)

    def stop(self):
        #"""Stop both wheels."""
        self.left_motor.stop()
        self.right_motor.stop()


    
class LineSensor:
    def __init__(self, pin):
        #"""Initialize a light sensor."""
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)

    def read(self):
        #"""Read the sensor status (0 = Dark, 1 = Light)."""
        return self.pin.value()
    
wheels = Wheel((7,6), (4, 5))
sensors=[LineSensor(12),LineSensor(13),LineSensor(14),LineSensor(15)]

def sensor_status():
    status=[]
    for i in range(4):
        status.append(sensors[i].read())
        sleep(0.01)
    return status

def line_following():
    status = sensor_status()
    if status[0] == 0 and status[-1] == 0 :
        if status[1] == 1 :
            wheels.turn_right()  
        elif status[2] == 1 :
            wheels.turn_left()
        else :
            wheels.forward()





while True :
    line_following()
   

