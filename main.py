from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep 
from code_reader import QRCodeReader
from line_sensor import LineSensor
from distance_sensor import DistanceSensor
from machine import Pin, PWM, I2C
from navigate_joseph import navigate
from  routes import *
#import math
current_box_location = 1
distance_sensor=DistanceSensor()
code_reader=QRCodeReader()
wheels = Wheel((4,5),(7,6)) # Initialize the wheels (GP4, GP5 for left wheel, GP7, GP6 for right wheel) before the order was wrong
actuator = Actuator(8, 9) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)
# message_string=QRCodeReader.read_qr_code()
# destination=QRCodeReader.parse_qr_data(message_string)
sensors=[LineSensor(12),LineSensor(13),LineSensor(14),LineSensor(15)]
#go to depot ->use distance sensor to detect distance->scan QR code->pick up->navigate to destination->drop off->go back to depot  (during this have some number n to record the number of boxes loaded)->depo2
def sensor_status():
    status=[]
    for i in range(4):
        status.append(sensors[i].read())
        #print(f"Sensor {i+1}: {sensors[i].read()}")
        #sleep(0.01)
    return status

def line_following(direction=0, speed = 90):#line following function
    """Follow the line using the line sensors"""
    #print("Following the line...")
    #Output: TTL(Black for LOW output, White for HIGH output)
    #this is line following so junctions not included
    status = sensor_status()

    if status[0] == 0 and status[-1] == 0:
        if status[2] == 1 :
            wheels.turn_right(speed)
            
        elif status[1] == 1 :
            wheels.turn_left(speed)
        else:
            wheels.forward(speed)
            
def rotate_left(speed=60,angle=90):
        
        time = angle*0.609/speed
        wheels.stop()  # Stop before turning
        sleep(0.5)  # Short delay for stability
        wheels.rotate_left(speed)
        sleep(time) #rotate long enough first to make sure the car deviate enough
        #start_time = time.time()  # Start timing turn
        while True:
            wheels.rotate_left(speed)  # Rotate left
            status = sensor_status()  # Check sensor again
            if status[2] == 1:  # If back on track, stop turning
                wheels.stop()
                break

def rotate_right(speed=60,angle=90):
        time=angle*0.609/speed #leave some room for adjustment     
        wheels.stop()  # Stop before turning
        sleep(0.5)  # Short delay for stability
        wheels.rotate_right(speed)
        sleep(time) #rotate long enough first to make sure the car deviate enough
        while True:
            wheels.rotate_right(speed)  # Rotate right
            status = sensor_status()  # Check sensor again
            if status[1] == 1:  # If back on track, stop turning
                wheels.stop()
                break

def rotate_180(direction = 1, speed = 60):
    wheels.stop()  # Stop before turning
    wheels.full_rotation(direction)
    sleep(0.609*180/speed) #rotate long enough first to make sure the car deviate enough
    while True:
        wheels.full_rotation(direction)  # Rotate anticlockwise
        status = sensor_status()  # Check sensor again
        if status[1+direction] == 1:  # If back on track, stop turning
            wheels.stop()
            break

def pickup():
    while True :
        line_following(speed=10)
        destination = code_reader.read_qr_code()
        if destination :
            rotate_180()
            destination = "d"+str(current_box_location)+destination
            return navigate(globals()[destination])
            


def go_to_depo1(): #go to depot 1 and return the destination
    """Navigate AGV to Depot 1"""
    n=0
    while True:
        status=sensor_status()
        line_following()
        if status[0] == 1 and status[-1]== 1:
            rotate_right()
            sleep(1)
            n+=1 #number of rotations
        if n==2 and distance_sensor.read()<=25:#didn't remember whether the distance sensor returns a number
            wheels.stop()
            destination=code_reader.parse_qr_data(code_reader.read_qr_code())
            return destination

def navigate_to(destination,pickup_location="Depot 1",):
    """Navigate AGV based on pickup location."""
    n = 0  # Track the number of times status[-1] is triggered
    if pickup_location == "Depot 1":  # Right side
        if destination == "A":
            wheels.stop()
            sleep(20)
            rotate_right(angle=180)
            while True:  # Loop until reaching the destination
                status = sensor_status()  # Read current sensor status
                line_following()  # Execute line-following, in the reverse direction first
                if status[0] == 1:
                    wheels.stop()
                    sleep(3)
                    if n in [0]: # Execute left rotation only at the 1st occurrence of status[0] == 1, use in list so more convenient to adjust and add if necessary
                        rotate_left()
                        sleep(1)  # Adjust timing if necessary
                        n += 1  # Update turn count
                    else:
                        n+=1
                        continue
                if status[-1] == 1:
                    rotate_right()
                if status[0]==1 and status[-1]==1:
                    wheels.stop()
                    return destination  # Arrived at A's doorstep
        elif destination == "B":
            while True:
                status = sensor_status()
                line_following()
                if status[-1] == 1:
                    if n in [1]:
                        rotate_right()
                        n+=1
                    else:
                        n+=1
                        continue
                if status[0] == 1:
                    rotate_left()
                    return destination
        elif destination == "C":
            while True:
                status = sensor_status()
                line_following()
                if status[-1] == 1:
                    if n in [1,2]:
                        rotate_right()
                        n+=1
                    else:
                        n+=1
                        continue
                if status[0] == 1:
                    rotate_left()
                    return destination
        elif destination == "D":
            while True:
                status = sensor_status()
                line_following()
                if status[-1] == 1:
                    if n in [2]:
                        rotate_right()
                        n+=1
                    else:
                        n+=1
                        continue
                if status[0] == 1:
                    rotate_left()
                    return destination
    elif pickup_location == "Depot 2":  # Left side
        if destination == "A":
            #the planned path
            pass
        elif destination == "B":
            #the planned path
            pass
        elif destination == "C":
            #the planned path
            pass
        elif destination == "D":
            #the planned path
            pass

def go_back(destination, pickup_location): #get destination from navigate_to, return the destination for the next box, may need to use dict for route reversal, harcoding again for now
    turn_count = 0
    if pickup_location == "Depot 1":  # Right side
        if destination == "A":
            while True: #first go reverse
                status=sensor_status()
                if status[0]==1 or status[-1]==1:
                    wheels.stop()
                    sleep(1)
                    wheels.rotate_left()
                    sleep(1)
                    break
                else:
                    wheels.reverse()
                    sleep(1)
            while True:#conditions may change
                status=sensor_status()
                line_following()
                # if status[0]==1 and status[-1]==1:
                #     wheels.rotate_left()
                #     sleep(1)
                if status[-1] == 1 and turn_count in [1]: # Execute left rotation only at the 1st occurrence of status[0] == 1, use in list so more convenient to adjust and add if necessary
                    turn_count += 1  # Update turn count
                    if turn_count==2:
                        wheels.rotate_right()
                        sleep(1)
                        if n==2 and distance_sensor.read()<=25:#didn't remember whether the distance sensor returns a number
                            destination=code_reader.parse_qr_data(code_reader.read_qr_code())
                            return destination
        elif destination == "B":
            #the planned path
            pass
        elif destination == "C":
            pass
            #the planned path
        elif destination == "D":
            pass
            #the planned path

    elif pickup_location == "Depot 2":  # Left side
        if destination == "A":
            pass
            #the planned path
        elif destination == "B":
            pass
            #the planned path
        elif destination == "C":
            pass
            #the planned path
        elif destination == "D":
            #the planned path
            pass

def drop_off():
    """Retract actuator to drop off the box"""
    while True:
        status=sensor_status()
        line_following()
        if status[0]==1 and status[-1]==1:
            wheels.stop()
            sleep(1)
            break
    actuator.retract(60)  # Retract actuator at 60% speed
    sleep(2)

def main():
    destination=go_to_depo1()
    n=4
    for i in range(n):
        pickup()
        wheels.rotate_right()
        sleep(1) #rotate 90 degrees
        navigate_to("Depot 1",destination)
        drop_off()
        sleep(2) 
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
