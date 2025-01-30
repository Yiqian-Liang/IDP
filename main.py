from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep
from code_reader import QRCodeReader
from line_sensor import LineSensor
wheels = Wheel((7,6), (4, 5))
#navigation function
message_string=QRCodeReader.read_qr_code()
destination=QRCodeReader.parse_qr_data(message_string)
sensor1=LineSensor(12)
sensor2=LineSensor(13)
sensor3=LineSensor(14)
sensor4=LineSensor(15)
sensors=[sensor1,sensor2,sensor3,sensor4]
def sensor_status():
    status=[]
    for i in range(4):
        status.append(sensors[i].read())
        #print(f"Sensor {i+1}: {sensors[i].read()}")
        sleep(0.1)
    return status
def line_following():
    """Follow the line using the line sensors"""
    #print("Following the line...")
    #Output: TTL(Black for LOW output, White for HIGH output)
    #this is line following so junctions not included
    while True:
        status = sensor_status()
        if status == [0, 0, 0, 0]:  # All sensors are on the line, move forward
            wheels.forward(80)
        elif status == [0, 0, 1, 0]:  # left_shifted, need to turn right
            wheels.turn_right(40)
        elif status == [0, 1, 0, 0]:  # right_shifted, need to turn left
            wheels.turn_left(40)
        elif status == [0, 0, 1, 0]:  # Only sensor 3 is off the line
            #print("Sensor 3 off line. Turning slightly left...")
            wheels.turn_left(40)

def navigate_to(destination, pickup_location):
    """Navigate AGV based on pickup location"""
    #print(f"Navigating to {destination} from {pickup_location}...")

    if pickup_location == "Depot 1":  # Right side
        if destination == "A":
            while True:#conditions may change
                line_following()
                if sensor1.read() == 1 and sensor2.read() == 1:
                    turn_left(70)
                    sleep(1)#may need to change the secs
                if sensor2.read() == 1 and sensor3.read() == 1:
                    break #arrive at A doorstep
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