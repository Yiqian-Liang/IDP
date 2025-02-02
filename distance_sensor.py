#Distance Sensor VL53L0X with Pico
#accurate range ~50-60cm
from machine import Pin, I2C  
import time
import vl53l0x
class DistanceSensor:
    def __init__(self, i2c=I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)):
        self.i2c = i2c
        self.tof = vl53l0x.VL53L0X(i2c)

    def read(self):
        return self.tof.read()

print("Successfully imported!")

# Initialize I2C (Pins: SCL=GP5, SDA=GP4)
i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)  

# Initialize VL53L0X sensor
tof = vl53l0x.VL53L0X(i2c)

print("VL53L0X ToF Sensor Initialized")

while True:
    distance = tof.read()  # Read distance in mm
    print("Distance: {:.2f} cm".format(distance / 10))  # Convert to cm
    time.sleep(0.5)  # Delay for stability
