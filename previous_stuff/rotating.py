#this is the test code for roatation
from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep 
#import time
#from code_reader import QRCodeReader
from line_sensor import LineSensor
#from distance_sensor import DistanceSensor
from machine import Pin, PWM, I2C
#distance_sensor=DistanceSensor()
#code_reader=QRCodeReader()
wheels = Wheel((4,5),(7,6))
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
        #sleep(0.05)
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
def main():
#     while True:
#         wheels.rotate_left()
    """Main loop for line following and turning logic."""
    while True:
        status = sensor_status()
        line_following(status)  # Follow the line

        # Detect a junction (both left and right sensors detect the line)
        if status[0] == 1 or status[-1] == 1:
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

            #end_time = time.time()  # End timing turn
            #print(f"Time taken to rotate 90 degrees: {end_time - start_time} sec")

            #wheels.forward(80)  # Resume forward motion

if __name__ == "__main__":
    main()


