#QR Code Reader(refined)
# the range is ~25-35 cm
import struct
from time import sleep
import machine

# Constants
TINY_CODE_READER_I2C_ADDRESS = 0x0C  # Device I2C address
TINY_CODE_READER_DELAY = 0.05        # Polling interval
TINY_CODE_READER_LENGTH_OFFSET = 0
TINY_CODE_READER_LENGTH_FORMAT = "H"
TINY_CODE_READER_MESSAGE_OFFSET = TINY_CODE_READER_LENGTH_OFFSET + struct.calcsize(TINY_CODE_READER_LENGTH_FORMAT)
TINY_CODE_READER_MESSAGE_SIZE = 254
TINY_CODE_READER_MESSAGE_FORMAT = "B" * TINY_CODE_READER_MESSAGE_SIZE
TINY_CODE_READER_I2C_FORMAT = TINY_CODE_READER_LENGTH_FORMAT + TINY_CODE_READER_MESSAGE_FORMAT
TINY_CODE_READER_I2C_BYTE_COUNT = struct.calcsize(TINY_CODE_READER_I2C_FORMAT)

# I2C setup for the Pico
i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4), freq=400000)

# Task queue
task_queue = []


def read_qr_code():
    """Read QR code and extract information"""
    try:
        read_data = i2c.readfrom(TINY_CODE_READER_I2C_ADDRESS, TINY_CODE_READER_I2C_BYTE_COUNT)
        message_length, = struct.unpack_from(TINY_CODE_READER_LENGTH_FORMAT, read_data, TINY_CODE_READER_LENGTH_OFFSET)
        message_bytes = struct.unpack_from(TINY_CODE_READER_MESSAGE_FORMAT, read_data, TINY_CODE_READER_MESSAGE_OFFSET)

        if message_length == 0:
            return None

        # Decode the message string
        message_string = bytearray(message_bytes[0:message_length]).decode("utf-8")
        print(f"QR Code Data: {message_string}")

        return message_string
    except Exception as e:
        print(f"Error reading QR Code: {e}")
        return None


def parse_qr_data(qr_data):
    """Parse QR code data and extract destination"""
    if qr_data and len(qr_data) > 0:
        destination = qr_data[0]  # The first character represents the destination
        if destination in ["A", "B", "C", "D"]:
            print(f"Destination identified: {destination}")
            return destination
    print("Invalid QR Code data")
    return None


def add_task(destination):
    """Add task to the queue"""
    if destination:
        task_queue.append(destination)
        print(f"Task added: Deliver to {destination}")


def get_next_task():
    """Retrieve the next task"""
    if task_queue:
        return task_queue.pop(0)  # Retrieve the first task in the queue
    return None


def navigate_to(destination):
    """Navigate AGV to the target location"""
    print(f"Navigating to {destination}...")

    if destination == "A":
        move_forward(2)
        turn_left()
        move_forward(2)
    elif destination == "B":
        move_forward(2)
        turn_right()
        move_forward(2)
    elif destination == "C":
        move_forward(2)
        turn_left()
        move_forward(1)
        turn_left()
        move_forward(2)
    elif destination == "D":
        move_forward(2)
        turn_right()
        move_forward(1)
        turn_right()
        move_forward(2)

    print(f"Arrived at {destination}")


def deliver_package():
    """Execute package delivery"""
    print("Delivering package...")
    sleep(2)
    print("Package delivered!")


# Main task loop
import time

start_time = time.time()
RUN_TIME = 300  # 5-minute runtime

while time.time() - start_time < RUN_TIME:
    qr_data = read_qr_code()
    destination = parse_qr_data(qr_data)
    if destination:
        add_task(destination)

    next_task = get_next_task()
    if next_task:
        navigate_to(next_task)
        deliver_package()

print("Task finished, returning to start...")
