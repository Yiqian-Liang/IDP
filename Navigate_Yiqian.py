from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep 
from code_reader import QRCodeReader
from line_sensor import LineSensor
from distance_sensor import DistanceSensor
from machine import Pin, PWM, I2C,Timer

distance_sensor=DistanceSensor()
code_reader=QRCodeReader()
wheels = Wheel((4,5),(7,6)) # Initialize the wheels (GP4, GP5 for left wheel, GP7, GP6 for right wheel) before the order was wrong
actuator = Actuator(8, 9) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)
sensors=[LineSensor(12),LineSensor(13),LineSensor(14),LineSensor(15)]
direction=0
forward_speed=80
rotate_speed=60
routes=[{"start_to_D1":[],"A":[[(1,0),lambda:rotate(direction="left")], [(1,0),None], [(0,1),lambda:rotate(direction="right")],[(1,1),wheels.stop],[(0,0),wheels.stop],[]]}]#use dict the first list value of the list is D1 to destination, the second list is D2 to destination, the third is destination to D1 the forth is destination to D2, and so on
button = Pin(22, Pin.IN, Pin.PULL_DOWN)
poll_timer=Timer(-1)
rpm_full_load=40
d_wheel=6.5/100 #in meters
D=0.19 #in meters ditance between the wheels

def junction_detected(pin):
    global junction_flag
    junction_flag = 1  # Set the flag when an interrupt occurs

# Timer callback for polling sensor status during line following.
# This callback checks the two middle sensors (sensors[1] and sensors[2])
# and sets the global 'direction' accordingly.
def sensor_callback(timer):
    global direction
    # If sensor[1] reads 1 and sensor[2] reads 0, then set direction to left.
    if sensors[1].read() == 1 and sensors[2].read() == 0:
        direction = 1
    # If sensor[2] reads 1 and sensor[1] reads 0, then set direction to right.
    elif sensors[2].read() == 1 and sensors[1].read() == 0:
        direction = 2
    else:
        direction = 0

# Functions to attach and detach the polling timer
def attach_polling():
    poll_timer.init(period=1, mode=Timer.PERIODIC, callback=sensor_callback)

def detach_polling():
    poll_timer.deinit()
    direction=0

# Simplified line following function that uses the global 'direction'
def line_following():
    attach_polling()
    if direction == 1:
        wheels.turn_left()
    elif direction == 2:
        wheels.turn_right()
    else:
        wheels.forward()

def attach_junction_interrupts(timer = None):
    sensors[0].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)
    sensors[-1].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)
def detach_junction_interrupts():
    sensors[0].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
    sensors[-1].pin.irq(trigger = Pin.IRQ_RISING, handler = None)

def safety_check(junction):#simple check if the junction matches what we expect
    if (sensors[0] == junction [0]) and (sensors[-1] == junction[-1]): #use 1 to represent error
        return 0
    else:
        return 1


def rotate(direction,speed=rotate_speed,angle=90):
    # status=sensor_status()
    # # Detect a junction (both left and right sensors detect the line)
    # if status[0] == 1 or status[-1] == 1:
        #print("Junction detected, turning...")
        detach_junction_interrupts()
        detach_polling() #may not need this
        rpm=speed*rpm_full_load/100
        w_wheel=rpm*2*3.14/60
        v_wheel=d_wheel*w_wheel/2
        w_ic=2*v_wheel/D
        time=angle*3.14*0.9/(180*w_ic) #leave some room for adjustment       
        wheels.stop()  # Stop before turning
        sleep(1)  # Short delay for stability
        wheels.rotate_left(speed)
        sleep(time) #rotate long enough first to make sure the car deviate enough
        #start_time = time.time()  # Start timing turn
        #Or attach all interrupts here, not sure
        attach_polling()
        if direction == "left":
            wheels.rotate_left(speed)
            if direction == 2:
                wheels.stop()
                sleep(1)
                #attach_junction_interrupts() 
        elif direction == "right":
            wheels.rotate_right(speed)
            if direction == 1:
                wheels.stop()
                sleep(1)
                #attach_junction_interrupts()

def navigate(route):
    n_steps = len(route)
    cur_step = 0
    global junction_flag,direction,poll_timer
    junction_flag = 0

    #Set up timer
    tim = Timer()

    #Assign interrupts that set the flag to be 1 if either sensor detects a line
    attach_junction_interrupts()
    #attach_polling()

    while button.value() == 0:
        pass

    # while junction_flag == 0:
    #     #First step just run continuous action
    #     route[cur_step][2]()

    while cur_step < n_steps-1:
        #When junction flag == 1
        #some sample route eg  [[(1,0),rotate_left], [(1,0),None], [(0,1),rotate_right()],[(1,1),wheels.stop]]
        if junction_flag == 1:
            #increment step (i.e. first step will be 0)           
            #Temporarily detach interrupts
            detach_junction_interrupts()
            detach_polling()
            junction_flag = 0
            while safety_check(route[cur_step][0]): #safety check fails
                line_following()
                pass
            if route[cur_step][1] is not None:
                route[cur_step][1]()
                cur_step += 1
            else:
                line_following()
                cur_step += 1
        else:
            #may just use the line following function here
            if distance_sensor.read() < 10: #extra safety not to crash
                wheels.stop()
            else:
                line_following()
            # if turning_direction == 1:
            #     wheels.turn_left()
            # elif turning_direction == 2:    
            #     wheels.turn_right()
            # else:
            #     wheels.forward() 


def pick_up_block(depo,distance_cm=5):
    detach_junction_interrupts()   
    while distance_sensor.read() >= distance_cm:
        line_following()
    detach_polling()
    wheels.stop()
    while True:
        if (data := code_reader.read()) is not None:                
            break
    actuator.extend()
    sleep(1)
    actuator.retract()
    sleep(1)
    if depo==1:
        rotate(direction="right",angle=180)
        attach_junction_interrupts()
    elif depo==2:
        rotate(direction="left",angle=180)
        attach_junction_interrupts()
        # if depo==1:
        #     rotate(direction="right",angle=180)
        # elif depo==2:
        #     rotate(direction="left",angle=180)
    return data

def drop_off_block(distance_cm):
        detach_junction_interrupts()
    #if distance_sensor.read() < distance_cm: #we may not need this
        detach_polling()
        wheels.stop()
        sleep(1)
        actuator.extend()
        sleep(1)
        actuator.retract()
        sleep(1)
        rotate(direction="right",angle=180) #left right both okay
        attach_polling()
        attach_junction_interrupts()
        # rotate(direction="left",angle=180)

#def last_action():
    #wheels.stop()
    #while button.value() == 0:
        #pass
    #navigate(test_route_Ad1)

#route for testing from depot 1 to A
test_route_d1A = [[(1,0),lambda:rotate(direction="left")], [(1,0),None], [(0,1),lambda:rotate(direction="right")],[(1,1),wheels.stop],[(0,0),wheels.stop]]
#test_route_Ad1 = [[None,None,line_following], [None, rotate_180, line_following],[None, rotate_left, line_following],[None,None,line_following],[None, rotate_right, wheels.stop]]

navigate(test_route_d1A)

def main():
    navigate(routes["start_to_D1"])
    n=4
    for i in range(n):
        data=pick_up_block(depo=1)
        navigate(routes[data][0])
        drop_off()
        sleep(2) 
        if i<n-1:
            navigate(routes[data][2])
        else:
           navigate(routes[data][3])
    for i in range(n):
        data=pick_up_block(depo=1)
        navigate(routes[data][0])
        drop_off()
        sleep(2) 
        if i<n-1:
            navigate(routes[data][2])
        else:
           navigate(routes[data][3])
if __name__ == "__main__":
    main()
