from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep 
from code_reader import QRCodeReader
from line_sensor import LineSensor
from distance_sensor import DistanceSensor
from machine import Pin, PWM, I2C
distance_sensor=DistanceSensor()
code_reader=QRCodeReader()
wheels = Wheel((7,6), (4, 5))
actuator = Actuator(8, 9) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)
#navigation function
# message_string=QRCodeReader.read_qr_code()
# destination=QRCodeReader.parse_qr_data(message_string)
sensors=[LineSensor(12),LineSensor(13),LineSensor(14),LineSensor(15)]
#go to depot ->use distance sensor to detect distance->scan QR code->pick up->navigate to destination->drop off->go back to depot  (during this have some number n to record the number of boxes loaded)->depo2
def main():
    destination=go_to_depo1()
    n=4
    for i in range(n):
        pickup()
        rotate_right()
        sleep(1) #rotate 90 degrees
        navigate_to("Depot 1",destination)
        drop_off()
        sleep(2) #rotate 180 degrees, sleep longer, may need to adjust
        if i<n-1:
            destination=go_back(destination,"Depot 1")
        else:
            destination=go_back(destination,"Depot 2")
    for i in range(n):
        pickup()
        navigate_to("Depot 2",destination)
        drop_off()
        if i<n-1:
            destination=go_back(destination,"Depot 2")
        else:
            go_back(destination,"Start Point")
if __name__ == "__main__":
    main()

def sensor_status():
    status=[]
    for i in range(4):
        status.append(sensors[i].read())
        #print(f"Sensor {i+1}: {sensors[i].read()}")
        sleep(0.1)
    return status
def line_following(status):#line following function
    """Follow the line using the line sensors"""
    #print("Following the line...")
    #Output: TTL(Black for LOW output, White for HIGH output)
    #this is line following so junctions not included
    #status=sensor_status()
    if status[0] == 0 and status[-1] == 0:
        if status[1] == 1 :
            wheels.turn_left()  # All sensors are on the line, move forward
        elif status[2] == 1 :
            wheels.turn_right()
        else:
            wheels.forward()
def pickup():
    """Extend actuator to pick up the box"""
    #before extending, we may need to use the distance sensor and the wheels to adjust the distance
    actuator.extend(60)  # Extend actuator at 60% speed
    sleep(2)

def go_to_depo1(): #go to depot 1 and return the destination
    """Navigate AGV to Depot 1"""
    n=0
    while True:
        status=sensor_status()
        line_following(status)
        if status[0] == 1 and status[-1]== 1:
            wheels.rotate_right()
            sleep(1)
            n+=1 #number of rotations
        if n==2 and distance_sensor.read()<=25:#didn't remember whether the distance sensor returns a number
            destination=code_reader.parse_qr_data(code_reader.read_qr_code())
            return destination

def navigate_to(pickup_location, destination):
    """Navigate AGV based on pickup location."""
    n = 0  # Track the number of times status[0] is triggered
    if pickup_location == "Depot 1":  # Right side
        if destination == "A":
            while True:  # Loop until reaching the destination
                status = sensor_status()  # Read current sensor status
                line_following(status)  # Execute line-following
                if status[0] == 1 and turn_count in [0]: # Execute left rotation only at the 1st occurrence of status[0] == 1, use in list so more convenient to adjust and add if necessary
                    rotate_left()
                    sleep(1)  # Adjust timing if necessary
                    n += 1  # Update turn count
                elif status[0] == 1:
                    n += 1  # Count the occurrence without turning
                if status[-1] == 1:  # If status[-1] == 1, it indicates arrival at the destination
                    rotate_right()  # Final adjustment
                    sleep(1)  
                    return destination  # Arrived at A's doorstep
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

def go_back(destination, pickup_location): #get destination from navigate_to, return the destination for the next box, may need to use dict for route reversal, harcoding again for now
    turn_count = 0
    if pickup_location == "Depot 1":  # Right side
        if destination == "A":
            rotate_left()#not sure about this
            sleep(2) #180 degrees?
            while True:#conditions may change
                status=sensor_status()
                line_following(status)
                if status[0]==1 and status[-1]==1:
                    rotate_left()
                    sleep(1)
                if status[-1] == 1 and turn_count in [1]: # Execute left rotation only at the 1st occurrence of status[0] == 1, use in list so more convenient to adjust and add if necessary
                    turn_count += 1  # Update turn count
                    if turn_count==2:
                        rotate_right()
                        sleep(1)
                        if n==2 and distance_sensor.read()<=25:#didn't remember whether the distance sensor returns a number
                            destination=code_reader.parse_qr_data(code_reader.read_qr_code())
                            return destination
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

def drop_off():
    """Retract actuator to drop off the box"""
    actuator.retract(60)  # Retract actuator at 60% speed
    sleep(2)

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
