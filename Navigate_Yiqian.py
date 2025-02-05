from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep 
from code_reader import QRCodeReader
from line_sensor import LineSensor
from distance_sensor import DistanceSensor
from machine import Pin, PWM, I2C,Timer
poll_timer=Timer(-1)
distance_sensor=DistanceSensor()
code_reader=QRCodeReader()
wheels = Wheel((4,5),(7,6)) # Initialize the wheels (GP4, GP5 for left wheel, GP7, GP6 for right wheel) before the order was wrong
actuator = Actuator(8, 9) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)
sensors=[LineSensor(12),LineSensor(13),LineSensor(14),LineSensor(15)]
direction=0
forward_speed=80
rotate_speed=60
routes=[{"start_to_D1":[],"A":[[(1,0),lambda:rotate(direction="left")], [(1,0),None], [(0,1),lambda:rotate(direction="right")],[(1,1),wheels.stop]]}]#and so on
button = Pin(22, Pin.IN, Pin.PULL_DOWN)
turning_flag= False
def junction_detected(pin):
    global junction_flag
    junction_flag = 1  # Set the flag when an interrupt occurs

flag = False

def sensor_callback(timer):
    global flag
    # 检查传感器状态，如果满足条件则置 flag
    if sensor[1].read() == 1 or sensor[2].read()==1
        flag = True
        if sensor[1].read==1:
            direction=1
        elif sensor[2].read()==1:
            direction==1
    else:
        flag = False
        direction=0

# 初始化定时器，每 1ms 调用一次 sensor_callback
poll_timer = Timer(-1)
poll_timer.init(period=1, mode=Timer.PERIODIC, callback=sensor_callback)





def attach_junction_interrupts(timer = None):
    sensors[0].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)
    sensors[-1].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)
def unnattach_junction_interrupts():
    sensors[0].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
    sensors[-1].pin.irq(trigger = Pin.IRQ_RISING, handler = None)

def attach_turning_interrupts(timer=None):
    sensors[1].pin.irq(trigger=Pin.IRQ_RISING, handler=turning)
    sensors[2].pin.irq(trigger=Pin.IRQ_RISING, handler=turning)
def unnattach_turning_interrupts():
    sensors[1].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
    sensors[2].pin.irq(trigger = Pin.IRQ_RISING, handler = None)

def safety_check(junction):
    #simple check if the junction matches what we expect
    if (sensors[0] == junction [0]) and (sensors[-1] == junction[-1]): #use 1 to represent error
        return 0
    else:
        return 1


def rotate(direction,speed=rotate_speed,angle=90):
    # status=sensor_status()
    # # Detect a junction (both left and right sensors detect the line)
    # if status[0] == 1 or status[-1] == 1:
        #print("Junction detected, turning...")
        unnattach_junction_interrupts()
        rpm_full_load=40
        rpm=speed*rpm_full_load/100
        d_wheel=6.5/100 #in meters
        w_wheel=rpm*2*3.14/60
        D=0.19 #in meters ditance between the wheels
        v_wheel=d_wheel*w_wheel/2
        w_ic=2*v_wheel/D
        time=angle*3.14*0.9/(180*w_ic) #leave some room for adjustment       
        wheels.stop()  # Stop before turning
        sleep(1)  # Short delay for stability
        wheels.rotate_left(speed)
        sleep(time) #rotate long enough first to make sure the car deviate enough
        #start_time = time.time()  # Start timing turn
        attach_turning_interrupts(timer=None)
        #Or attach all interrupts here, not sure
        if direction == "left":
            wheels.rotate_left(speed)
            if turning_direction == 2:
                wheels.stop()
                sleep(1)
                attach_junction_interrupts() 
        elif direction == "right":
            wheels.rotate_right(speed)
            if turning_direction == 1:
                wheels.stop()
                sleep(1)
                attach_junction_interrupts()

def navigate(route):
    n_steps = len(route)
    cur_step = 0
    global junction_flag,turning_flag, turning_direction
    junction_flag = 0

    #Set up timer
    tim = Timer()

    #Assign interrupts that set the flag to be 1 if either sensor detects a line
    attach_junction_interrupts()
    attach_turning_interrupts()

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
            #Temporarily unnattach interrupts
            unnattach_junction_interrupts()
            unnattach_turning_interrupts()
            junction_flag = 0
            while safety_check(route[cur_step][0]): #safety check fails
                #do something
                pass
            if route[cur_step][1] is not None:
                route[cur_step][1]()
                cur_step += 1
            else:
                line_following()
                cur_step += 1
        else:
            #may just use the line following function here
            line_following()
            # if turning_direction == 1:
            #     wheels.turn_left()
            # elif turning_direction == 2:    
            #     wheels.turn_right()
            # else:
            #     wheels.forward() 


def pick_up_block(distance_cm,depo):
    unnattach_junction_interrupts()
    if distance_sensor.read() < distance_cm:#we may not need this
        unnattach_turning_interrupts()
        wheels.stop()
        while True:
            if (data := code_reader.read()) is not None:                
                break
        actuator.extend()
        sleep(1)
        actuator.retract()
        sleep(1)
        attach_turning_interrupts()
        attach_junction_interrupts()
        if depo==1:
            rotate_right(angle=180)
        elif depo==2:
            rotate_left(angle=180)
        return data

def drop_off_block(distance_cm):
        unnattach_junction_interrupts()
    #if distance_sensor.read() < distance_cm: #we may not need this
        unnattach_turning_interrupts()
        wheels.stop()
        sleep(1)
        actuator.extend()
        sleep(1)
        actuator.retract()
        sleep(1)
        attach_turning_interrupts()
        attach_junction_interrupts()
        rotate_left(angle=180)

def last_action():
    wheels.stop()
    while button.value() == 0:
        pass
    navigate(test_route_Ad1)

#route for testing from depot 1 to A
test_route_d1A = [[(1,0),lambda:rotate(direction="left")], [(1,0),None], [(0,1),lambda:rotate(direction="right")],[(1,1),wheels.stop]]
#test_route_Ad1 = [[None,None,line_following], [None, rotate_180, line_following],[None, rotate_left, line_following],[None,None,line_following],[None, rotate_right, wheels.stop]]

navigate(test_route_d1A)
routes=[]
def main():
    navigate(start_to_D1)
    n=4
    for i in range(n):
        pick_up_block()
        rotate_right(angle=180)
        navigate()
        drop_off()
        sleep(2) 
        if i<n-1:
            destination=navigate(destination,"Depot 1")
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