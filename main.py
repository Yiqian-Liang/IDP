from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep 
from sensors import QRCodeReader, DistanceSensor, LineSensor, LED, Button
from machine import Pin, PWM, I2C,Timer

#---------------------- Set up motors
wheels = Wheel((7,6),(4,5)) # Initialize the wheels (GP4, GP5 for left wheel, GP7, GP6 for right wheel) before the order was wrong
actuator = Actuator(8, 9) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)

#-----------------------Set up sensors
distance_sensor=DistanceSensor()
code_reader=QRCodeReader()
sensors=[LineSensor(18),LineSensor(19),LineSensor(20),LineSensor(21)]
button = Button(pin = 14) #push button
crash_sensor = Button(pin = 12)
Set_LED = LED(pin = 17)

'''
#These assignments are outdated - the new configuration as per Owen's circuit board is above
distance_sensor=DistanceSensor()
code_reader=QRCodeReader()
wheels = Wheel((7,6),(4,5)) #wheels changed # Initialize the wheels (GP4, GP5 for left wheel, GP7, GP6 for right wheel) before the order was wrong
actuator = Actuator(8, 9) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)
sensors=[LineSensor(12),LineSensor(13),LineSensor(14),LineSensor(15)]
'''

direction=0
forward_speed=80
rotate_speed=60
forward_distance=5/100 #5cm
routes = {
    "D2_to_start": [],
    "start_to_D1": [
        [(1, 1), None],  # Move straight from start position
        [(1, 1), lambda: rotate(direction="right")],  # Turn left at the first junction
        [(1, 1), lambda: rotate(direction="right")],  # Turn right at the second junction
        #[(0, 0), wheels.stop]  # Stop at D1
    ],
    "A": [
        [  # D1 to A
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), None],
            [(0, 1), lambda: rotate(direction="right")],
            #[(1, 1), wheels.stop]
        ],
        [  # A to D1
            [(1, 1), lambda: rotate(direction="left")],
            [(0, 1), None],
            [(0, 1), lambda: rotate(direction="right")],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to A
            [(0, 1), lambda: rotate(direction="right")],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 1), wheels.stop]
        ],
        [  # A to D2
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 0), lambda: rotate(direction="left")],
            #[(0, 0), wheels.stop]
        ]
    ],
    "B": [
        [  # D1 to B
            [(1, 0), None],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 1), wheels.stop]
        ],
        [  # B to D1
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 1), lambda: rotate(direction="right")],
            [(0, 1), None],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to B
            [(0, 1), None],
            [(0, 1), lambda: rotate(direction="right")],
            [(1, 0), None],
            [(0, 1), lambda: rotate(direction="right")],
            [(1, 1), wheels.stop]
        ],
        [  # B to D2
            [(1, 1), lambda: rotate(direction="left")],
            [(0, 1), None],
            [(0, 1), lambda: rotate(direction="left")],
            [(0, 1), None],
            #[(0, 0), wheels.stop]
        ]
    ],
    "C": [
        [  # D1 to C
            [(1, 0), None],
            [(1, 0), None],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), None],
            [(1, 0), lambda: rotate(direction="left")],
            [(0, 1), lambda: rotate(direction="right")],
            [(1, 1), wheels.stop]
        ],
        [  # C to D1
            [(1, 1), lambda: rotate(direction="left")],
            [(1, 1), lambda: rotate(direction="right")],
            [(0, 1), None],
            [(1, 0), lambda: rotate(direction="right")],
            [(0, 1), None],
            [(0, 1), None],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to C
            [(0, 1), None],
            [(0, 1), lambda: rotate(direction="right")],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 1), wheels.stop]
        ],
        [  # C to D2
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 1), lambda: rotate(direction="left")],
            [(0, 1), None],
            #[(0, 0), wheels.stop]
        ]
    ],
    "D": [
        [  # D1 to D
            [(1, 0), None],
            [(1, 0), None],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 1), wheels.stop]
        ],
        [  # D to D1
            [(1, 1), lambda: rotate(direction="right")],
            [(0, 1), lambda: rotate(direction="right")],
            [(0, 1), None],
            [(0, 1), None],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to D
            [(0, 1), None],
            [(0, 1), None],
            [(0, 1), lambda: rotate(direction="right")],
            [(0, 1), None],
            [(0, 1), lambda: rotate(direction="right")],
            [(1, 1), wheels.stop]
        ],
        [  # D to D2
            [(1, 1), lambda: rotate(direction="left")],
            [(1, 0), None],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), None],
            [(1, 0), None],
            #[(0, 0), wheels.stop]
        ]
    ]
}

# Use dict: 
# - The first list is from D1 to the destination.
# - The second list is from the destination to D1.
# - The third list is from D2 to the destination.
# - The fourth list is from the destination to D2, and so on.

#button = Pin(22, Pin.IN, Pin.PULL_DOWN) #now included at top with other sensors

def junction_detected(pin):
    global junction_flag
    junction_flag = 1  # Set the flag when an interrupt occurs

# Timer callback for polling sensor status during line following.
# This callback checks the two middle sensors (sensors[1] and sensors[2])
# and sets the global 'direction' accordingly.

# Simplified line following function that uses the global 'direction'
def line_following():
    if sensors[2].read() == 1:
        wheels.turn_right()
    elif sensors[1].read() == 1:
        wheels.turn_left()
    else:
        wheels.forward()

def attach_junction_interrupts(timer = None):
    sensors[0].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)
    sensors[-1].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)
def detach_junction_interrupts():
    sensors[0].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
    sensors[-1].pin.irq(trigger = Pin.IRQ_RISING, handler = None)

def safety_check(junction):#simple check if the junction matches what we expect
    if (sensors[0] == junction [0]) and (sensors[-1] == junction[-1]): #use 0 to represent error
        return 1
    else:
        return 0


def rotate(direction,speed=rotate_speed,angle=90):
    # # Detect a junction (both left and right sensors detect the line)
    # if status[0] == 1 or status[-1] == 1:
        #print("Junction detected, turning...")
        detach_junction_interrupts()
        #detach_polling() #may not need this
        rpm=speed*rpm_full_load/100
        w_wheel=rpm*2*3.14/60
        v_wheel=d_wheel*w_wheel/2
        #w_ic=2*v_wheel/D
        w_ic=v_wheel/D
        time=angle*3.14*0.4/(180*w_ic) #leave some room for adjustment
        forward_time=forward_distance/v_wheel
        print(time)
        wheels.stop()  # Stop before turning
        sleep(3)  # Short delay for stability
        wheels.forward(speed)  # Start moving forward
        sleep(forward_time)
        wheels.stop()
        sleep(3)
        if direction == "left":
            wheels.rotate_left(speed)
            sleep(time)
            while sensors[2].read() != 1:
                wheels.rotate_left(speed)
            wheels.stop()
            sleep(3)               
                #attach_junction_interrupts() 
        elif direction == "right":
            wheels.rotate_right(speed)
            sleep(time)
            while sensors[1].read() != 1:
                wheels.rotate_right(speed)
            wheels.stop()
            sleep(3)
                
def full_rotation(direction,speed=rotate_speed,angle=180):
    # status=sensor_status()
    # # Detect a junction (both left and right sensors detect the line)
    # if status[0] == 1 or status[-1] == 1:
        #print("Junction detected, turning...")
        detach_junction_interrupts()
        #detach_polling() #may not need this
        rpm=speed*rpm_full_load/100
        w_wheel=rpm*2*3.14/60
        v_wheel=d_wheel*w_wheel/2
        w_ic=2*v_wheel/D
        #w_ic=v_wheel/D
        time=angle*3.14*0.8/(180*w_ic) #leave some room for adjustment
        #forward_time=forward_distance/v_wheel
        print(time)
        wheels.stop()  # Stop before turning
        sleep(3)  # Short delay for stability
        wheels.full_rotation(direction=direction,speed=speed) #0 for anticlockwise, 1 for clockwise
        sleep(time)
        while sensors[1].read() != 1 and sensors[2].read() != 1:
            wheels.full_rotation(speed)
        wheels.stop()
        sleep(3)

def navigate(route):
    n_steps = len(route)
    cur_step = 0
    global junction_flag,direction,poll_timer
    junction_flag = 0

    #Set up timer
    tim = Timer()

    #Assign interrupts that set the flag to be 1 if either sensor detects a line
    attach_junction_interrupts()

    while button.read() == 0:
        pass

    # while junction_flag == 0:
    #     #First step just run continuous action
    #     route[cur_step][2]()

    while cur_step < n_steps:
        if junction_flag == 1 and safety_check(route[cur_step][0]): 
            print(junction_flag)
            wheels.stop()
            sleep(1)
            # while safety_check(route[cur_step][0]): #safety check fails
            #     junction_flag = 0
            #     line_following()
            #     if junction_flag == 1:
            #         continue
            #     pass
            detach_junction_interrupts()
            #detach_polling()
            junction_flag = 0
            if route[cur_step][1] is not None:
                route[cur_step][1]()
                cur_step += 1
                attach_junction_interrupts()
            else:
                line_following()
                attach_junction_interrupts()
                cur_step += 1
        else:
            #may just use the line following function here
#             if distance_sensor.read() < 10: #extra safety not to crash
#                 wheels.stop()
#             else:
            line_following()
    wheels.stop()
    sleep(1)

# Timer callback for polling sensor status during line following.
# This callback checks the two middle sensors (sensors[1] and sensors[2])
# and sets the global 'direction' accordingly.



def attach_button_interrupt():
    button.pin.irq(trigger = Pin.IRQ_RISING, handler = button_reset)
def detach_button_interrupt():
    button.pin.irq(trigger = Pin.IRQ_RISING, handler = None)

def button_reset():
    '''Can be pushed at any time to stop the robot, 
    then waits until robot is moved and replaced at start, then restarts code'''
    detach_button_interrupt()
    LED.stop_flash() #since won't be driving anymore
    wheels.stop()
    sleep(1) #definitely prevents bouncing
    while button.value() == 0:
        pass
    main() #go back to start of program



def pick_up_block(depo,distance_cm=5):
    detach_junction_interrupts()   
    while distance_sensor.read() >= distance_cm:
        line_following()
    wheels.stop()
    while True:
        if (data := code_reader.read()) is not None:                
            break
    actuator.extend()
    sleep(1)
    actuator.retract()
    sleep(1)
    if depo==1:
        full_rotation(direction=1)
        attach_junction_interrupts()
    elif depo==2:
        full_rotation(direction=0)
        attach_junction_interrupts()
        # if depo==1:
        #     rotate(direction="right",angle=180)
        # elif depo==2:
        #     rotate(direction="left",angle=180)
    return data

def drop_off(distance_cm):
        detach_junction_interrupts()
    #if distance_sensor.read() < distance_cm: #we may not need this
        detach_polling()
        wheels.stop()
        sleep(1)
        actuator.extend()
        sleep(1)
        actuator.retract()
        sleep(1)
        wheels.reverse()
        sleep(1) #need to adjust sleep time
        full_rotation() #left right both okay
        attach_junction_interrupts()
        # rotate(direction="left",angle=180)


def main():
    #this is for testing
    #Wait until button is pushed to start
    while button.value() == 0:
        pass

    LED.start_flash() #starts flashing as soon as starts first route
    while True:
        line_following()
    actuator.extend()
    
    navigate(routes["A"][0])
    navigate(routes["A"][1])
    print("code_reader.read()=",code_reader.read())
    pick_up_block(depo=1)
    drop_off(distance_cm=10)

#this is the actual main structure for the competition
    navigate(routes["start_to_D1"])
    n=4
    for i in range(n):
        data=pick_up_block(depo=1)
        navigate(routes[data][0])
        drop_off()
        sleep(2) 
        if i<n-1:
            navigate(routes[data][1])
        else:
           navigate(routes[data][3]) #destination to D2
    for i in range(n):
        data=pick_up_block(depo=1)
        navigate(routes[data][2])
        drop_off()
        sleep(2) 
        if i<n-1:
            navigate(routes[data][2])
        else:
           navigate(routes["D2_to_start"])
           LED.stop_flash() #stops flashing as soon as finished last route
if __name__ == "__main__":
    main()