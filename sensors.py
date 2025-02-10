from machine import Pin, I2C
import vl53l0x
import struct


#Distance Sensor VL53L0X with Pico
#accurate range ~50-60cm ~2.5cm larger than the actual distance,returns distance in mm, converting to cm in 1 decimal
class DistanceSensor:
    def __init__(self, i2c=I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)):
        self.i2c = i2c
        self.tof = vl53l0x.VL53L0X(i2c)

    def read(self):
        distance_mm=self.tof.read()
        distance_cm=round(distance_mm/10,2)
        return distance_cm

class QRCodeReader:
    """Class to handle QR Code reading via I2C on Raspberry Pi Pico."""
    
    I2C_ADDRESS = 0x0C  # Device I2C address
    DELAY = 0.05        # Polling interval
    LENGTH_OFFSET = 0
    LENGTH_FORMAT = "H"
    MESSAGE_OFFSET = LENGTH_OFFSET + struct.calcsize(LENGTH_FORMAT)
    MESSAGE_SIZE = 254
    MESSAGE_FORMAT = "B" * MESSAGE_SIZE
    I2C_FORMAT = LENGTH_FORMAT + MESSAGE_FORMAT
    I2C_BYTE_COUNT = struct.calcsize(I2C_FORMAT)

    def __init__(self, scl_pin=4, sda_pin=3, freq=400000):
        """Initialize I2C communication with the QR Code Reader."""
        self.i2c = machine.I2C(0, scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin), freq=freq)

    def read_qr_code(self):
        """Read QR code and return extracted information."""
        try:
            read_data = self.i2c.readfrom(self.I2C_ADDRESS, self.I2C_BYTE_COUNT)
            message_length, = struct.unpack_from(self.LENGTH_FORMAT, read_data, self.LENGTH_OFFSET)
            message_bytes = struct.unpack_from(self.MESSAGE_FORMAT, read_data, self.MESSAGE_OFFSET)

            if message_length == 0:
                return None

            # Decode the message string
            message_string = bytearray(message_bytes[0:message_length]).decode("utf-8")
            #print(f"QR Code Data: {message_string}")
            destination = message_string [0]  # The first character represents the destination
            if destination in ["A", "B", "C", "D"]:
                return destination

        except Exception as e:
            print(f"Error reading QR Code: {e}")
            return None

class LineSensor:
    def __init__(self, pin):
        """Initialize a line sensor."""
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)

    def read(self):
        """Read the sensor status (0 = Dark, 1 = Light)."""
        return self.pin.value()
        
class LED:
    def __init__(self, pin=17):
        self.pin = Pin(pin, Pin.OUT)

    def start_flash (self):
        self.pin.value(1)
    def stop_flash (self) :
        self.pin.value(0)

class Button:
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
    
    def read(self):
        """Read the sensor status (0 = not pushed, 1 = pushed)."""
        return self.pin.value()