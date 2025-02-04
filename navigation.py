#for testing the Navigation function
from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep 
#from code_reader import QRCodeReader
from line_sensor import LineSensor
#from distance_sensor import DistanceSensor
from machine import Pin, PWM, I2C
#distance_sensor=DistanceSensor()
#code_reader=QRCodeReader()
wheels = Wheel((4,5),(7,6)) # Initialize the wheels (GP4, GP5 for left wheel, GP7, GP6 for right wheel) before the order was wrong
actuator = Actuator(8, 9) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)
#navigation function
# message_string=QRCodeReader.read_qr_code()
# destination=QRCodeReader.parse_qr_data(message_string)
sensors=[LineSensor(12),LineSensor(13),LineSensor(14),LineSensor(15)]
#go to depot ->use distance sensor to detect distance->scan QR code->pick up->navigate to destination->drop off->go back to depot  (during this have some number n to record the number of boxes loaded)->depo2
def sensor_status():
    status=[]
    for i in range(4):
        status.append(sensors[i].read())
        #print(f"Sensor {i+1}: {sensors[i].read()}")
        #sleep(0.1)
    return status
def line_following(status,direction=0):#line following function
    """Follow the line using the line sensors"""
    #print("Following the line...")
    #Output: TTL(Black for LOW output, White for HIGH output)
    #this is line following so junctions not included
    #status=sensor_status()
    if direction==1:
        if status[0] == 0 and status[-1] == 0:
            if status[1] == 1 :
                wheels.turn_right(direction=1)
            elif status[2] == 1 :
                wheels.turn_left(direction=1)
            else:
                wheels.reverse()
    else:
        if status[0] == 0 and status[-1] == 0:
            if status[1] == 1 :
                wheels.turn_left()  # All sensors are on the line, move forward
            elif status[2] == 1 :
                wheels.turn_right()
            else:
                wheels.forward()

def rotate_left():
    # status=sensor_status()
    # # Detect a junction (both left and right sensors detect the line)
    # if status[0] == 1 or status[-1] == 1:
        #print("Junction detected, turning...")
        wheels.stop()  # Stop before turning
        sleep(2)  # Short delay for stability
        wheels.rotate_left(60)
        sleep(3.2) #rotate long enough first to make sure the car deviate enough
        #start_time = time.time()  # Start timing turn

        while True:
            wheels.rotate_left(40)  # Rotate left
            status = sensor_status()  # Check sensor again
            if status[2] == 1:  # If back on track, stop turning
                wheels.stop()
                sleep(0.5)
                break

def rotate_right():
    # status=sensor_status()
    # if status[0] == 1 or status[-1] == 1:
        #print("Junction detected, turning...")
        wheels.stop()  # Stop before turning
        sleep(2)  # Short delay for stability
        wheels.rotate_right(60)
        sleep(3.2) #rotate long enough first to make sure the car deviate enough
        #start_time = time.time()  # Start timing turn
        while True:
            wheels.rotate_right(40)  # Rotate right
            status = sensor_status()  # Check sensor again
            if status[1] == 1:  # If back on track, stop turning
                wheels.stop()
                sleep(0.5)
                break
def navigate_to(destination,pickup_location="Depot 1",):
    """Navigate AGV based on pickup location."""
    n = 0  # Track the number of times status[-1] is triggered
    if pickup_location == "Depot 1":  # Right side
        if destination == "A":
            while True:  # Loop until reaching the destination
                status = sensor_status()  # Read current sensor status
                line_following(status,1)  # Execute line-following, in the reverse direction first
                if status[-1] == 1:
                    if n in [0]: # Execute left rotation only at the 1st occurrence of status[0] == 1, use in list so more convenient to adjust and add if necessary
                        rotate_right()
                        sleep(1)  # Adjust timing if necessary
                        n += 1  # Update turn count
                    else:
                        n+=1
                        pass
                elif status[0] == 1:
                    return destination  # Arrived at A's doorstep
        elif destination == "B":
            while True:
                status = sensor_status()
                line_following(status,1)
                if status[-1] == 1:
                    if n in [1]:
                        rotate_right()
                        n+=1
                    else:
                        n+=1
                        pass
                elif status[0] == 1:
                    rotate_left()
                    return destination
        elif destination == "C":
            while True:
                status = sensor_status()
                line_following(status,1)
                if status[-1] == 1:
                    if n in [1,2]:
                        rotate_right()
                        n+=1
                    else:
                        n+=1
                        pass
                elif status[0] == 1:
                    rotate_left()
                    return destination
        elif destination == "D":
            while True:
                status = sensor_status()
                line_following(status,1)
                if status[-1] == 1:
                    if n in [2]:
                        rotate_right()
                        n+=1
                    else:
                        n+=1
                        pass
                elif status[0] == 1:
                    rotate_left()
                    return destination
def main():
    navigate_to("A")
if "name" == "__main__":
    main()