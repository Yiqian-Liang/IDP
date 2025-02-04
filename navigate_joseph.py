from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from line_sensor import LineSensor
from distance_sensor import DistanceSensor
from threading import Timer #To create timer interrupts
from machine import Pin, PWM, I2C
distance_sensor=DistanceSensor()
code_reader=QRCodeReader()
wheels = Wheel((4,5),(7,6))
actuator = Actuator(8, 9) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)
#navigation function
# message_string=QRCodeReader.read_qr_code()
# destination=QRCodeReader.parse_qr_data(message_string)
sensors=[LineSensor(12),LineSensor(13),LineSensor(14),LineSensor(15)]

def junction_detected(pin):
    global junction_flag
    junction_flag = 1  # Set the flag when an interrupt occurs

def attach_interrupts():
    sensors[0].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)
    sensors[-1].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)

def navigate(route):
    '''
    -Navigate takes an array of steps which make up the desired route.
    -Each step consists of an array as follows [safety check, turning action, continuous action]
    -If no turning action (e.g. want straight on) or no safety check (if doesn't work) use None
    -The safety action should include a desired configuration of the 2 junction sensors
    (e.g. [1,0] for left turn only, [1,1] for either...)
    -The turn action should be turn left, turn right or 180 degree spin
    -The continuous action should be one of 'pick up block', 'straight line follow' or 'place block'
    -The first action presumes that there is no safety check or turn action required,
    and will skip to the continuous action.
    '''

    n_steps = len(route)
    cur_step = 0
    global junction_flag 
    junction_flag = -1

    #Assign interrupts that set the flag to be 1 if either sensor detects a line
    attach_interrupts()

    while True:
        #When junction flag == 1
        if junction_flag == 1:
            #increment step (i.e. first step will be 0)
            cur_step += 1

            #Perform safety check on junction if necessary
            if route[cur_step][0] is not None:
                while safety_check(route[cur_step][0]) == 0:
                    #if failed check, maybe reverse?
                    pass
            
            #Carry out turning if necessary
            if route[cur_step][1] is not None :

                route[cur_step][1]()

                #Temporarily unnattach interrupts
                sensors[0].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
                sensors[-1].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
                junction_flag = 0

                #Set timer to reattach interrupts once moved away from junction
                #Junction recovery time may need adjusting
                Timer(0.5, attach_interrupts)

            elif route[cur_step][1] is None:
                Timer(0.5, attach_interrupts)
    
        else:
            while junction_flag != 1:
                #Perform continuous action until junction detected
                route[cur_step][2]()
                #The final action in the route should then call the next route
                #This will depend on previous location, number of deliveries etc




def safety_check(junction):
    #simple check if the junction matches what we expect
    if (sensors[0] == junction [0]) and (sensors[-1] == junction[-1]):
        return 1
    else:
        return 0
    

#Copied and pasted these from main for my use here----------------------------------------
#Should be removed later
def sensor_status():
    status=[]
    for i in range(4):
        status.append(sensors[i].read())
        #print(f"Sensor {i+1}: {sensors[i].read()}")
        sleep(0.01)
    return status
def line_following(status,direction=0):#line following function
    """Follow the line using the line sensors"""
    #print("Following the line...")
    #Output: TTL(Black for LOW output, White for HIGH output)
    #this is line following so junctions not included
    #status=sensor_status()
    if status[0] == 0 and status[-1] == 0:
        if status[2] == 1 :
            wheels.turn_right()
            
        elif status[1] == 1 :
            wheels.turn_left()
        else:
            wheels.forward()
            


def rotate_left(speed):
    # status=sensor_status()
    # # Detect a junction (both left and right sensors detect the line)
    # if status[0] == 1 or status[-1] == 1:
        #print("Junction detected, turning...")
        wheels.stop()  # Stop before turning
        sleep(1)  # Short delay for stability
        wheels.rotate_left(speed)
        sleep(3.2) #rotate long enough first to make sure the car deviate enough
        #start_time = time.time()  # Start timing turn
        while True:
            wheels.rotate_left(speed)  # Rotate left
            status = sensor_status()  # Check sensor again
            if status[2] == 1:  # If back on track, stop turning
                wheels.stop()
                sleep(0.05)
                break

def rotate_right(speed):
    # status=sensor_status()
    # if status[0] == 1 or status[-1] == 1:
        #print("Junction detected, turning...")
        wheels.stop()  # Stop before turning
        sleep(1)  # Short delay for stability
        wheels.rotate_right(speed)
        sleep(3.2) #rotate long enough first to make sure the car deviate enough
        #start_time = time.time()  # Start timing turn
        while True:
            wheels.rotate_right(speed)  # Rotate right
            status = sensor_status()  # Check sensor again
            if status[1] == 1:  # If back on track, stop turning
                wheels.stop()
                sleep(0.05)
                break

def rotate_180(direction):
    wheels.stop()  # Stop before turning
    wheels.full_rotation(direction)
    sleep(2) #rotate long enough first to make sure the car deviate enough
    #start_time = time.time()  # Start timing turn
    while True:
        wheels.full_rotation(direction)  # Rotate anticlockwise
        status = sensor_status()  # Check sensor again
        if status[1+direction] == 1:  # If back on track, stop turning
            wheels.stop()
            sleep(0.01)
            break


#route for testing from depot 1 to A
test_route_d1A = [[None, rotate_180, line_following], [None, rotate_right, line_following], [None, None, line_following],[None, rotate_right, line_following],[None, None, wheels.stop]]

navigate(test_route_d1A)

