from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep 
from sensors import QRCodeReader, DistanceSensor, LineSensor, LED, Button
from machine import Pin, PWM, I2C
from navigate_joseph import navigate
from  previous_stuff.routes_old import *

#---------------------- Set up motors
wheels = Wheel((4,5),(7,6)) # Initialize the wheels (GP4, GP5 for left wheel, GP7, GP6 for right wheel) before the order was wrong
actuator = Actuator(8, 9) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)

#-----------------------Set up sensors
distance_sensor=DistanceSensor()
code_reader=QRCodeReader()
sensors=[LineSensor(18),LineSensor(19),LineSensor(20),LineSensor(21)]
push_button = Button(pin = 14)
crash_sensor = Button(pin = 12)
Set_LED = LED(pin = 17)

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
            

if __name__ == "__main__":
    main()
