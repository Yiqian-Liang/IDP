import struct
import machine
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

    def __init__(self, scl_pin=1, sda_pin=0, freq=400000):
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
        

    
