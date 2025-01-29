from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep
from code_reader import QRCodeReader
#navigation function
message_string=QRCodeReader.read_qr_code()
destination=QRCodeReader.parse_qr_data(message_string)
def line_following():
    sensor1=
def navigate_to(destination, pickup_location):
    """Navigate AGV based on pickup location"""
    print(f"Navigating to {destination} from {pickup_location}...")

    if pickup_location == "Depot 1":  # Right side
        if destination == "A":
            #the planned path
        elif destination == "B":
            #the planned path
        elif destination == "C":
            #the planned path
        elif destination == "D":
            #the planned path

    elif pickup_location == "Depot 2":  # Left side
        if destination == "A":
            #the planned path
        elif destination == "B":
            #the planned path
        elif destination == "C":
            #the planned path
        elif destination == "D":
            #the planned path

    print(f"Arrived at {destination}")#may need to change the signal(like LED Flashing?)
# Initialize wheel motors (Left: GP6, GP7 | Right: GP4, GP5)
wheels = Wheel((7,6), (4, 5))

# Initialize linear actuator (GP8 for direction, GP9 for PWM control)
actuator = Actuator(8, 9)

# Example movement sequence
print("Moving forward...")
wheels.forward(80)  # Move forward at 80% speed
sleep(2)  # Move for 2 seconds

print("Turning left...")
wheels.turn_left(60)  # Turn left at 60% speed
sleep(1)

print("Rotating right...")
wheels.rotate_right(80)  # Rotate in place to the right
sleep(1)

print("Stopping wheels...")
wheels.stop()  # Stop both wheels

print("Extending actuator...")
actuator.extend(60)  # Extend actuator at 60% speed
sleep(2)

print("Retracting actuator...")
actuator.retract(60)  # Retract actuator at 60% speed
sleep(2)

print("Stopping actuator...")
actuator.stop()  # Stop the actuator