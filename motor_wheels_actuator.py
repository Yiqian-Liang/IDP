from machine import Pin, PWM

# ---------------- Generic Motor Class ---------------- #
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


# ---------------- Wheel Class (Inherits from Motor) ---------------- #
class Wheel(Motor):
    def __init__(self, left_pins, right_pins):
        """Wheel class for two-wheel robot movement."""
        super().__init__(*left_pins)  # Left wheel
        self.right_wheel = Motor(*right_pins)  # Right wheel

    def forward(self, speed=80):
        """Move forward at the specified speed."""
        self.set_direction(0)  # Left wheel forward
        self.right_wheel.set_direction(0)  # Right wheel forward
        self.set_speed(speed)
        self.right_wheel.set_speed(speed)

    def reverse(self, speed=80):
        """Move backward at the specified speed."""
        self.set_direction(1)
        self.right_wheel.set_direction(1)
        self.set_speed(speed)
        self.right_wheel.set_speed(speed)

    def turn_left(self, speed=80):
        """Turn left (reduce left wheel speed, keep right wheel moving)."""
        self.set_direction(0)  # Left wheel forward
        self.right_wheel.set_direction(0)  # Right wheel forward
        self.set_speed(speed / 2)  # Reduce left wheel speed
        self.right_wheel.set_speed(speed)

    def turn_right(self, speed=80):
        """Turn right (reduce right wheel speed, keep left wheel moving)."""
        self.set_direction(0)
        self.right_wheel.set_direction(0)
        self.set_speed(speed)
        self.right_wheel.set_speed(speed / 2)

    def rotate_left(self, speed=80):
        """Rotate left in place (left wheel backward, right wheel forward)."""
        self.set_direction(1)  # Left wheel backward
        self.right_wheel.set_direction(0)  # Right wheel forward
        self.set_speed(speed)
        self.right_wheel.set_speed(speed)

    def rotate_right(self, speed=80):
        """Rotate right in place (left wheel forward, right wheel backward)."""
        self.set_direction(0)
        self.right_wheel.set_direction(1)
        self.set_speed(speed)
        self.right_wheel.set_speed(speed)

    def stop(self):
        """Stop both wheels."""
        super().stop()
        self.right_wheel.stop()


# ---------------- Actuator Class (Inherits from Motor) ---------------- #
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


