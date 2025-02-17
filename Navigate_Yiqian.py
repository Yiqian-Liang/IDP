from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep 
from sensors import QRCodeReader, DistanceSensor, LineSensor, LED, Button
from machine import Pin, PWM, I2C,Timer

#---------------------- Set up motors
wheels = Wheel((7,6),(4,5)) # Initialize the wheels (GP7, GP6 for left wheel, GP4, GP5 for right wheel) before the order was wrong
actuator = Actuator(3, 2) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)

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
d_wheel=6.5/100 #in meters
D=0.19 #in meters ditance between the wheels
direction=0
forward_speed=80
rotate_speed=60
forward_distance=5/100 #5cm
reverse_speed=40
actuator_speed=80
extension=14 #12.7mm
drop_off_distance=10 #10cm
actuator_max_speed=7 #7mm/s
rpm_full_load=40 #rpm=speed*rpm_full_load/100
routes = {
    "D2": [
        [  # Start to D2
            [3, None],  # Move straight from start position
            [3, lambda: rotate(direction="left")],  # Turn left at the first junction
            [2, None],  # Move straight from start position
            [3, lambda: rotate(direction="left")],  # Turn right at the second junction
        ],
        [  # D2 to start
            [2, lambda: rotate(direction="left")], #imagine has just arrived at D2 instead of has actually picked up anything
            [1, None],
            [2, lambda: rotate(direction="right")],
            [3, wheels.stop]
        ],
    ],
    "D1": [
        [  # Start to D1
            [3, None],  # Move straight from start position
            [3, lambda: rotate(direction="right")],  # Turn left at the first junction
            [3, lambda: rotate(direction="right")],  # Turn right at the second junction
        ],
        [  # D1 to start
            [1, lambda: rotate(direction="left")],
            [1, lambda: rotate(direction="left")],
            [3, wheels.stop]
        ],
    ],
    "A": [
        [  # D1 to A
            [1, lambda: rotate(direction="left")],
            [1, None],
            [2, lambda: rotate(direction="right")],
            [3, wheels.stop]
        ],
        [  # A to D1
            [3, lambda: rotate(direction="left")],
            [2, None],
            [2, lambda: rotate(direction="right")],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to A
            [2, lambda: rotate(direction="right")],
            [1, lambda: rotate(direction="left")],
            [3, wheels.stop]
        ],
        [  # A to D2
            [3, lambda: rotate(direction="right")],
            [1, lambda: rotate(direction="left")],
            #[(0, 0), wheels.stop]
        ]
    ],
    "B": [
        [  # D1 to B
            [1, None],
            [1, lambda: rotate(direction="left")],
            [1, lambda: rotate(direction="left")],
            [3, wheels.stop]
        ],
        [  # B to D1
            [3, lambda: rotate(direction="right")],
            [3, lambda: rotate(direction="right")],
            [2, None],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to B
            [2, None],
            [2, lambda: rotate(direction="right")],
            [1, None],
            [2, lambda: rotate(direction="right")],
            [3, wheels.stop]
        ],
        [  # B to D2
            [3, lambda: rotate(direction="left")],
            [2, None],
            [2, lambda: rotate(direction="left")],
            [2, None],
            #[(0, 0), wheels.stop]
        ]
    ],
    "C": [
        [  # D1 to C
            [1, None],
            [1, None],
            [1, lambda: rotate(direction="left")],
            [1, None],
            [1, lambda: rotate(direction="left")],
            [2, lambda: rotate(direction="right")],
            [3, wheels.stop]
        ],
        [  # C to D1
            [3, lambda: rotate(direction="left")],
            [3, lambda: rotate(direction="right")],
            [2, None],
            [1, lambda: rotate(direction="right")],
            [2, None],
            [2, None],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to C
            [2, None],
            [2, lambda: rotate(direction="right")],
            [1, lambda: rotate(direction="left")],
            [1, lambda: rotate(direction="left")],
            [3, wheels.stop]
        ],
        [  # C to D2
            [3, lambda: rotate(direction="right")],
            [3, lambda: rotate(direction="right")],
            [3, lambda: rotate(direction="left")],
            [2, None],
            #[(0, 0), wheels.stop]
        ]
    ],
    "D": [
        [  # D1 to D
            [1, None],
            [1, None],
            [1, lambda: rotate(direction="left")],
            [1, lambda: rotate(direction="left")],
            [3, wheels.stop]
        ],
        [  # D to D1
            [3, lambda: rotate(direction="right")],
            [2, lambda: rotate(direction="right")],
            [2, None],
            [2, None],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to D
            [2, None],
            [2, None],
            [2, lambda: rotate(direction="right")],
            [2, None],
            [2, lambda: rotate(direction="right")],
            [3, wheels.stop]
        ],
        [  # D to D2
            [3, lambda: rotate(direction="left")],
            [1, None],
            [1, lambda: rotate(direction="left")],
            [1, None],
            [1, None],
            #[(0, 0), wheels.stop]
        ]
    ]
}

routes = {
    "D2": [
        [  # Start to D2
            [(1, 1), None],  # Move straight from start position
            [(1, 1), lambda: rotate(direction="left")],  # Turn left at the first junction
            [(0, 1), None],  # Move straight from start position
            [(1, 1), lambda: rotate(direction="left")],  # Turn right at the second junction
        ],
        [  # D2 to start
            [(0, 1), lambda: rotate(direction="left")], #imagine has just arrived at D2 instead of has actually picked up anything
            [(1, 0), None],
            [(0, 1), lambda: rotate(direction="right")],
            [(1, 1), wheels.stop]
        ],
    ],
    "D1": [
        [  # Start to D1
            [(1, 1), None],  # Move straight from start position
            [(1, 1), lambda: rotate(direction="right")],  # Turn left at the first junction
            [(1, 1), lambda: rotate(direction="right")],  # Turn right at the second junction
        ],
        [  # D1 to start
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 1), wheels.stop]
        ],
    ],
    "A": [
        [  # D1 to A
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), None],
            [(0, 1), lambda: rotate(direction="right")],
            [(1, 1), wheels.stop]
        ],
        [  # A to D1
            #[(1, 1), wheels.stop],
            [(1, 1), lambda: rotate(direction="right")],
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
        ],
        [  # A to Start
            [(1, 1), lambda: rotate(direction="left")],
            [(1, 0), lambda: rotate(direction="right")],
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
        ],
        [  # B to start
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 1), lambda: rotate(direction="right")],
            [(0, 1), lambda: rotate(direction="left")],
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


def speed_and_time(speed,distance_cm=6):
    rpm=speed*rpm_full_load/100
    w_wheel=rpm*2*3.14/60
    v_wheel=d_wheel*w_wheel/2
    time=distance_cm/(v_wheel*100)
    return v_wheel,time
def extend(speed=actuator_speed): #extend actuator
    time=extension/(actuator_max_speed*speed/100)
    actuator.extend(speed)
    sleep(time)
    actuator.stop()
def retract(speed=actuator_speed): #retract actuator
    time=extension/(actuator_max_speed*speed/100)*1.25 #EXTRA FOR SAFETY
    actuator.retract(speed)
    sleep(time)
    actuator.stop()

# Use dict: 
# - The first list is from D1 to the destination.
# - The second list is from the destination to D1.
# - The third list is from D2 to the destination.
# - The fourth list is from the destination to D2, and so on.

#button = Pin(22, Pin.IN, Pin.PULL_DOWN) #now included at top with other sensors

def junction_detected(pin):
    global junction_flag
    if sensors[0].read() == 1 and sensors[-1].read() == 0:
        junction_flag = 1
    elif sensors[0].read() == 0 and sensors[-1].read() == 1:
        junction_flag = 2
    elif sensors[0].read() == 1 and sensors[-1].read() == 1:
        junction_flag = 3 

# Timer callback for polling sensor status during line following.
# This callback checks the two middle sensors (sensors[1] and sensors[2])
# and sets the global 'direction' accordingly.

# Simplified line following function that uses the global 'direction'
def line_following(direction=direction,speed=forward_speed):
    if direction == 0:
        if sensors[2].read() == 1:
            wheels.turn_right(speed=speed,direction=direction)
        elif sensors[1].read() == 1:
            wheels.turn_left(speed=speed,direction=direction)
        else:
            wheels.forward(speed=speed,direction=direction)
    else:
        if sensors[2].read() == 1:
            wheels.turn_right(speed)
        elif sensors[1].read() == 1:
            wheels.turn_left(speed=speed,direction=direction)
        else:
            wheels.reverse(speed=speed)

def attach_junction_interrupts(timer = None):
    sensors[0].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)
    sensors[-1].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)
def detach_junction_interrupts():
    sensors[0].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
    sensors[-1].pin.irq(trigger = Pin.IRQ_RISING, handler = None)




def rotate(direction,speed=rotate_speed,angle=90):
    # # Detect a junction (both left and right sensors detect the line)
    # if status[0] == 1 or status[-1] == 1:
        #print("Junction detected, turning...")
        detach_junction_interrupts()
        #detach_polling() #may not need this
        v_wheel=speed_and_time(speed=speed,distance_cm=6)[0]
        #w_ic=2*v_wheel/D
        w_ic=v_wheel/D
        time=angle*3.14*0.8/(180*w_ic) #leave some room for adjustment
        forward_time=forward_distance/v_wheel
        print(time)
        wheels.stop()  # Stop before turning
        #sleep(3)  # Short delay for stability
        wheels.forward(speed)  # Start moving forward
        sleep(forward_time)
        wheels.stop()
        #sleep(3)
        if direction == "left":
            wheels.rotate_left(speed)
            sleep(time)
            while sensors[2].read() != 1:
                wheels.rotate_left(speed)
            wheels.stop()
            #sleep(3)               
                #attach_junction_interrupts() 
        elif direction == "right":
            wheels.rotate_right(speed)
            sleep(time)
            while sensors[1].read() != 1:
                wheels.rotate_right(speed)
            wheels.stop()
            #sleep(3)

def full_rotation(direction,speed=rotate_speed,angle=180): #need to rotate faster got load
    # status=sensor_stastus()
    # # Detect a junction (both left and right sensors detect the line)
    # if status[0] == 1 or status[-1] == 1:
        #print("Junction detected, turning...")
        detach_junction_interrupts()
        v_wheel=speed_and_time(speed)[0]
        w_ic=2*v_wheel/D
        #w_ic=v_wheel/D
        time=angle*3.14*0.8/(180*w_ic) #leave some room for adjustment
        #forward_time=forward_distance/v_wheel
        print(time)
        wheels.stop()  # Stop before turning
        sleep(3)  # Short delay for stability
        wheels.full_rotation(speed)
        sleep(time)
        if direction == 0:
            while sensors[2].read() != 1:
                wheels.full_rotation(speed)
        elif direction == 1:
            while sensors[1].read() != 1:
                wheels.full_rotation(speed)

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
        if junction_flag == route[cur_step][0]():
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
            tim.init(period=500, mode=Timer.ONE_SHOT, callback=attach_junction_interrupts)
    wheels.stop()
    #sleep(1)

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



def pick_up_block(a, depo=1, speed=80, d_rev=7, d_safe=6.5):
    # Compute wheel speed parameters based on safe distance.
    v_wheel, t_safe = speed_and_time(speed, d_safe)
    # Initial setup: perform actuator retraction and extension.
#     retract(100)
#     extend(100)  
    # Reverse for a preset duration (rev_time should be defined globally).
    
    data1 = None
    data2 = None
    attempt=2

    # Main loop: continue until a valid QR code is detected.
    while True:
        # Inner loop: while the distance sensor reading is above the safe threshold,
        # perform line following.
        while distance_sensor.read() >= d_safe:
            line_following(speed=speed)  # Execute line following.
            if data1 is None:
                data1 = code_reader.read_qr_code()  # Attempt to read QR code.
            # If a valid QR code is detected, save it and break out of the inner loop.
            if data1 in ['A', 'B', 'C', 'D']:
                data2 = data1
                continue
        # If a valid QR code was detected, print it and exit the main loop.
        if data2 in ['A', 'B', 'C', 'D']:
            print("QR Code Detected:", data2)
            break
        else:
            attempt += 1
            # If the robot reaches the safe distance without detecting a QR code,
            # reverse for a calculated duration and then try again.
            if attempt > 2:
                data2='A'
                continue #if we can't read just deliver to A(cloest point)
            _, t_safe = speed_and_time(speed, d_safe)
            wheels.reverse(speed)
            sleep(t_safe)
            wheels.stop()
    # Continue with any subsequent actions (e.g., moving forward, rotating, etc.)           
    # Fine adjustment: reverse slowly for a short distance.
    #_, t_adjust = speed_and_time(speed/2, d_safe/5)
    wheels.reverse(40)
    #sleep(t_adjust)   
    # Retract actuator and then move forward.
    retract()
    wheels.stop()
    if a > 2:
        _, t_reverse = speed_and_time(speed, (a - 2.5) * d_rev)
        wheels.reverse(speed)
        sleep(t_reverse)
        wheels.stop()
        sleep(2)
    # Rotate 180° based on depo parameter.
    if depo == 1:
        full_rotation(1)  # Rotate right.
    elif depo == 2:
        full_rotation(0)  # Rotate left.
    return data2
def drop_off_block():
    detach_junction_interrupts()
#    extend()
#     junction_flag=0
#     tim=Timer()
#     #tim.init(period=500, mode=Timer.ONE_SHOT, callback=attach_junction_interrupts)
#     wheels.reverse(speed=50)
#     sleep(speed_and_time(50, 6)[1])
    wheels.reverse(50)
    sleep(2)
    while True:
        wheels.reverse(50)
        if sensors[-1].read()==1 or sensors[0].read()==1:
            break
    wheels.stop()



routes = { #(1,0)->1 (0,1)->2 (1,1)->3
    "D2_to_start": [],
    "start_to_D1": [
        [3, None],  # Move straight from start position
        [3, lambda: rotate(direction="right")],  # Turn left at the first junction
        [3, lambda: rotate(direction="right")],  # Turn right at the second junction
        #[(0, 0), wheels.stop]  # Stop at D1
    ],
    "A": [
        [  # D1 to A
            [1, lambda: rotate(direction="left")],
            [1, None],
            [2, lambda: rotate(direction="right")],
            #[3, wheels.stop]
        ],
        [  # A to D1
            [2, None],
            [2, lambda: rotate(direction="right")],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to A
            [2, lambda: rotate(direction="right")],
            [1, lambda: rotate(direction="left")],
            [3, wheels.stop]
        ],
        [  # A to D2
            [1, lambda: rotate(direction="left")],
            #[(0, 0), wheels.stop]
        ]
    ],
    "B": [
        [  # D1 to B
            [1, None],
            [1, lambda: rotate(direction="left")],
            [1, lambda: rotate(direction="left")],
            [3, wheels.stop]
        ],
        [  # B to D1
            [3, lambda: rotate(direction="right")],
            [2, None],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to B
            [2, None],
            [2, lambda: rotate(direction="right")],
            [1, None],
            [2, lambda: rotate(direction="right")],
            [3, wheels.stop]
        ],
        [  # B to D2
            [2, None],
            [2, lambda: rotate(direction="left")],
            [2, None],
            #[(0, 0), wheels.stop]
        ]
    ],
    "C": [
        [  # D1 to C
            [1, None],
            [1, None],
            [1, lambda: rotate(direction="left")],
            [1, None],
            [1, lambda: rotate(direction="left")],
            [2, lambda: rotate(direction="right")],
            [3, wheels.stop]
        ],
        [  # C to D1
            [3, lambda: rotate(direction="right")],
            [2, None],
            [1, lambda: rotate(direction="right")],
            [2, None],
            [2, None],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to C
            [2, None],
            [2, lambda: rotate(direction="right")],
            [1, lambda: rotate(direction="left")],
            [1, lambda: rotate(direction="left")],
            [3, wheels.stop]
        ],
        [  # C to D2
            [3, lambda: rotate(direction="right")],
            [3, lambda: rotate(direction="left")],
            [2, None],
            #[(0, 0), wheels.stop]
        ]
    ],
    "D": [
        [  # D1 to D
            [1, None],
            [1, None],
            [1, lambda: rotate(direction="left")],
            [1, lambda: rotate(direction="left")],
            [3, wheels.stop]
        ],
        [  # D to D1
            [2, lambda: rotate(direction="right")],
            [2, None],
            [2, None],
            #[(0, 0), wheels.stop]
        ],
        [  # D2 to D
            [2, None],
            [2, None],
            [2, lambda: rotate(direction="right")],
            [2, None],
            [2, lambda: rotate(direction="right")],
            [3, wheels.stop]
        ],
        [  # D to D2
            [1, None],
            [1, lambda: rotate(direction="left")],
            [1, None],
            [1, None],
            #[(0, 0), wheels.stop]
        ]
    ]
}
def drop_off_block(data,speed=50,depo=1): #another version of drop off block, if reverse is reliable enough
    #if distance_sensor.read() < distance_cm: #we may not need this
    detach_junction_interrupts()
    while time.time()-start < speed_and_time(speed)[1]:  #may use fixed values
        line_following(speed)
    #print(time.time()-speed_and_time(speed)[1])
    wheels.stop()
    '''above is for extra distance of forward line following(calibration) may be able to remove'''
    extend()
    attach_junction_interrupts()
    retract()
    for i in range(2):
        while junction_flag == 0:
            wheels.reverse(speed)
        junction_flag = 0
        detach_junction_interrupts()
        tim.init(period=500, mode=Timer.ONE_SHOT, callback=attach_junction_interrupts)
    if data in ["C"]:
        rotate(direction="left")
    else:
        if data=="A":
            if depo==1:
                rotate(direction="right")
            else:
                rotate(direction="left")
        if data in ["B","D"]:
            if depo==1:
                rotate(direction="right")
            else:
                rotate(direction="left")
def main():
    #Wait until button is pushed to start
    while button.read() == 0:
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
    navigate(routes["start_to_D1"])
    n=4
    for i in range(n):
        data=pick_up_block(a=i,depo=1)
        navigate(routes[data][0])
        drop_off()
        #drop_off_block(data)
        sleep(2) 
        if i<n-1:
            navigate(routes[data][1])
        else:
           navigate(routes[data][3]) #destination to D2
    for i in range(n):
        data=pick_up_block(a=i,depo=1)
        navigate(routes[data][2])
        drop_off()
        #drop_off_block(data)
        sleep(2) 
        if i<n-1:
            navigate(routes[data][2])
        else:
           navigate(routes["D2_to_start"])
           LED.stop_flash() #stops flashing as soon as finished last route
if __name__ == "__main__":
    main()