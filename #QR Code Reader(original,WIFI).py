#QR Code Reader(original,WIFI) 
#the range is ~25-35 cm
import network
import struct
from time import sleep
import machine

# Constants
TINY_CODE_READER_I2C_ADDRESS = 0x0C  # The code reader's I2C ID (hex 0C, decimal 12)
TINY_CODE_READER_DELAY = 0.05        # Pause duration between sensor polls
TINY_CODE_READER_LENGTH_OFFSET = 0
TINY_CODE_READER_LENGTH_FORMAT = "H"
TINY_CODE_READER_MESSAGE_OFFSET = TINY_CODE_READER_LENGTH_OFFSET + struct.calcsize(TINY_CODE_READER_LENGTH_FORMAT)
TINY_CODE_READER_MESSAGE_SIZE = 254
TINY_CODE_READER_MESSAGE_FORMAT = "B" * TINY_CODE_READER_MESSAGE_SIZE
TINY_CODE_READER_I2C_FORMAT = TINY_CODE_READER_LENGTH_FORMAT + TINY_CODE_READER_MESSAGE_FORMAT
TINY_CODE_READER_I2C_BYTE_COUNT = struct.calcsize(TINY_CODE_READER_I2C_FORMAT)

# I2C setup for the Pico (update pins as needed for your board)
i2c = machine.I2C(
    0,
    scl=machine.Pin(5),
    sda=machine.Pin(4),
    freq=400000
)

# Connect to Wi-Fi
def connect(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('Waiting for connection...')
        sleep(1)
    return wlan

# Uncomment this line to see detected peripherals on the I2C bus
# print(i2c.scan())  # Expected output: [12] (sensor's ID)

# Main loop to read person sensor results and process Wi-Fi QR codes
while True:
    sleep(TINY_CODE_READER_DELAY)

    # Read data from the sensor
    read_data = i2c.readfrom(TINY_CODE_READER_I2C_ADDRESS, TINY_CODE_READER_I2C_BYTE_COUNT)

    # Extract message length and bytes
    message_length, = struct.unpack_from(TINY_CODE_READER_LENGTH_FORMAT, read_data, TINY_CODE_READER_LENGTH_OFFSET)
    message_bytes = struct.unpack_from(TINY_CODE_READER_MESSAGE_FORMAT, read_data, TINY_CODE_READER_MESSAGE_OFFSET)

    if message_length == 0:
        continue

    try:
        # Decode message as a UTF-8 string
        message_string = bytearray(message_bytes[0:message_length]).decode("utf-8")

        # Process Wi-Fi provisioning text
        if message_string.startswith("WIFI:"):
            message_parts = message_string[5:].split(";")
            wifi_ssid = None
            wifi_password = None

            # Parse SSID and password from message
            for part in message_parts:
                if part == "":
                    continue
                key, value = part.split(":")
                if key == "S":
                    wifi_ssid = value
                elif key == "P":
                    wifi_password = value

            # Attempt Wi-Fi connection
            wlan = connect(wifi_ssid, wifi_password)
            if wlan.isconnected():
                break
        else:
            print(f"Couldn't interpret '{message_string}' as a Wi-Fi network name and password")
    except:
        print("Couldn't decode as UTF-8")
        pass

# Post-connection tasks
print("Connected!")
print(wlan.ifconfig())