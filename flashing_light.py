from machine import Pin

class LED:
    def __init__(self, pin=17):
        self.pin = Pin(pin, Pin.OUT)

    def start_flash (self):
        self.pin.value(1)
    def stop_flash (self) :
        self.pin.value(0)

        