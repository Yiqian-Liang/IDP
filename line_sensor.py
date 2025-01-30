from machine import Pin, PWM
class LineSensor:
    def __init__(self, pin):
        """Initialize a light sensor."""
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)

    def read(self):
        """Read the sensor status (0 = Dark, 1 = Light)."""
        return self.pin.value()
