#Ultrasonic Distance Sensor
#Somehow large error ~5-10 cm
from machine import ADC, Pin
import time

# Constants
MAX_DISTANCE = 520  # Maximum measurable distance (cm)
VCC = 3.3  # Power supply voltage
ADC_MAX_VALUE = 65535  # 16-bit ADC range (for Raspberry Pi Pico)

# Define ADC pin (Use GPIO26, corresponding to ADC0)
sensor_pin = ADC(Pin(26))  # Equivalent to A0 on Arduino

print("URM09 Ultrasonic Sensor Initialized")

while True:
    # Read raw ADC value (0-65535)
    adc_value = sensor_pin.read_u16()
    
    # Convert ADC value to voltage
    voltage = (adc_value / ADC_MAX_VALUE) * VCC

    # Convert voltage to distance (based on sensor formula)
    distance = (voltage * MAX_DISTANCE) / VCC

    # Print the measured distance
    print("Distance: {:.2f} cm".format(distance))
    
    time.sleep(0.5)  # Delay for stability
