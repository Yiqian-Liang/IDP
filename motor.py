from machine import Pin, PWM

# ---------------- Motor Class (Generic for all motors) ---------------- #
class Motor:
    def __init__(self, dir_pin, pwm_pin, freq=1000):
        """Generic Motor class for controlling all types of motors."""
        self.dir = Pin(dir_pin, Pin.OUT)  # Direction control
        self.pwm = PWM(Pin(pwm_pin))  # PWM speed control
        self.pwm.freq(freq)  # Set PWM frequency
        self.pwm.duty_u16(0)  # Initialize speed to 0

    def set_speed(self, speed):
        """Set motor speed (0-100%)."""
        self.pwm.duty_u16(int(65535 * speed / 100))

    def set_direction(self, direction):
        """Set motor direction (0 = forward, 1 = reverse)."""
        self.dir.value(direction)

    def stop(self):
        """Stop the motor."""
        self.pwm.duty_u16(0)


# ---------------- Wheel Class (Controls two wheels) ---------------- #
class Wheel:
    def __init__(self, left_pins, right_pins):
        """Wheel class for two-wheel robot movement."""
        self.left_motor = Motor(*left_pins)  # Left wheel motor
        self.right_motor = Motor(*right_pins)  # Right wheel motor

    def forward(self, speed=90):
        """Move both wheels forward."""
        self.left_motor.set_direction(0)
        self.right_motor.set_direction(0)
        self.left_motor.set_speed(speed)
        self.right_motor.set_speed(speed)

    def reverse(self, speed=40):
        """Move both wheels backward."""
        self.left_motor.set_direction(1)
        self.right_motor.set_direction(1)
        self.left_motor.set_speed(speed)
        self.right_motor.set_speed(speed)

    def turn_left(self, speed=60, direction=0):
        """Turn left (slow down left wheel, keep right wheel moving)."""
        if direction==1:
            self.left_motor.set_direction(direction)  
            self.right_motor.set_direction(direction)  
            self.left_motor.set_speed(speed+10)
            self.right_motor.set_speed(speed-10)
        else:
            self.left_motor.set_direction(direction)  
            self.right_motor.set_direction(direction)
            self.right_motor.set_speed(speed+10)  
            self.left_motor.set_speed(speed-10)  # Reduce left wheel speed

    def turn_right(self, speed=60, direction=0):
        """Turn right (slow down right wheel, keep left wheel moving)."""
        if direction==1:
            self.left_motor.set_direction(direction)
            self.right_motor.set_direction(direction)
            self.right_motor.set_speed(speed+10)
            self.left_motor.set_speed(speed-10)
        else:
            self.left_motor.set_direction(direction)
            self.right_motor.set_direction(direction)
            self.left_motor.set_speed(speed+10)
            self.right_motor.set_speed(speed-10)  # Reduce right wheel speed

    def full_rotation(self,direction, speed = 60 ) : #anticlockwise is 1 and clockwise is 0
        self.left_motor.set_speed(speed)
        self.right_motor.set_speed(speed) 
        if direction == 0 :#rotate anticlockwise
           self.left_motor.set_direction(1)
           self.right_motor.set_direction(0)
        else :#rotate clockwise
           self.left_motor.set_direction(0)
           self.right_motor.set_direction(1)


    def rotate_left(self, speed=60):
        # Rotate left (left wheel backward, right wheel forward).
        self.left_motor.set_direction(1)
        self.right_motor.set_direction(0)
        self.left_motor.set_speed(speed)
        self.right_motor.set_speed(speed)

    def rotate_right(self, speed=60):
        # Rotate right (left wheel forward, right wheel backward
        self.right_motor.set_direction(1)
        self.left_motor.set_direction(0)
        self.left_motor.set_speed(speed)
        self.right_motor.set_speed(speed)

    def stop(self):
        """Stop both wheels."""
        self.left_motor.stop()
        self.right_motor.stop()


# ---------------- Actuator Class (For linear movement) ---------------- #
class Actuator(Motor):
    def __init__(self, dir_pin, pwm_pin):
        """Actuator class for controlling a linear actuator."""
        super().__init__(dir_pin, pwm_pin)
    

    def extend(self, speed=80):
        """Extend the actuator."""
        self.set_direction(1)  # Move forward (extend)
        self.set_speed(speed)

    def retract(self, speed=80):
        """Retract the actuator."""
        self.set_direction(0)  # Move backward (retract)
        self.set_speed(speed)

    def stop(self):
        """Stop the actuator."""
        super().stop()




