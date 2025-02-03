#Distance Sensor VL53L0X with Pico
#accurate range ~50-60cm ~2.5cm larger than the actual distance,returns distance in mm, converting to cm in 1 decimal
from machine import Pin, I2C  
import time
import vl53l0x
class DistanceSensor:
    def __init__(self, i2c=I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)):
        self.i2c = i2c
        self.tof = vl53l0x.VL53L0X(i2c)

    def read(self):
        distance_mm=self.tof.read()
        distance_cm=round(distance_mm/10,2)
        return distance_cm

#print("Successfully imported!")

#test code
# # Initialize I2C (Pins: SCL=GP5, SDA=GP4)
# i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)  

# # Initialize VL53L0X sensor
# tof = vl53l0x.VL53L0X(i2c)

# print("VL53L0X ToF Sensor Initialized")

# while True:
#     distance = tof.read()  # Read distance in mm
#     print("Distance: {:.2f} cm".format(distance / 10))  # Convert to cm
#     time.sleep(0.5)  # Delay for stability
