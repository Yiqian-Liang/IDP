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

    def turn_left(self, speed=90):
        """Turn left (slow down left wheel, keep right wheel moving)."""
        self.left_motor.set_direction(0)  
        self.right_motor.set_direction(0)  
        self.left_motor.set_speed(speed-10)  # Reduce left wheel speed
        self.right_motor.set_speed(speed+10)

    def turn_right(self, speed=90):
        """Turn right (slow down right wheel, keep left wheel moving)."""
        self.left_motor.set_direction(0)
        self.right_motor.set_direction(0)
        self.left_motor.set_speed(speed+10)
        self.right_motor.set_speed(speed-10)  # Reduce right wheel speed

    def rotate_left(self, speed=60):
        """Rotate left in place (left wheel backward, right wheel forward)."""
        self.left_motor.set_direction(1)
        self.right_motor.set_direction(0)
        self.left_motor.set_speed(speed/2)
        self.right_motor.set_speed(speed)

    def rotate_right(self, speed=60):
        """Rotate right in place (left wheel forward, right wheel backward)."""
        self.left_motor.set_direction(0)
        self.right_motor.set_direction(1)
        self.left_motor.set_speed(speed)
        self.right_motor.set_speed(speed/2)

    def stop(self):
        """Stop both wheels."""
        self.left_motor.stop()
        self.right_motor.stop()


# ---------------- Actuator Class (For linear movement) ---------------- #
class Actuator(Motor):
    def __init__(self, dir_pin, pwm_pin, min_position=0, max_position=100):
        """Actuator class for controlling a linear actuator."""
        super().__init__(dir_pin, pwm_pin)
        self.position = min_position  # Track current position
        self.min_position = min_position
        self.max_position = max_position

    def extend(self, speed=80):
        """Extend the actuator."""
        if self.position < self.max_position:
            self.set_direction(0)  # Move forward (extend)
            self.set_speed(speed)
            self.position += 1  # Simulate position change

    def retract(self, speed=80):
        """Retract the actuator."""
        if self.position > self.min_position:
            self.set_direction(1)  # Move backward (retract)
            self.set_speed(speed)
            self.position -= 1  # Simulate position change

    def stop(self):
        """Stop the actuator."""
        super().stop()