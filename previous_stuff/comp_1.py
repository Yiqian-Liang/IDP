from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep 
from sensors import QRCodeReader, DistanceSensor, LineSensor, LED, Button
from machine import Pin, PWM, I2C,Timer, reset

#---------------------- Set up motors
wheels = Wheel((7,6),(4,5)) # Initialize the wheels (GP4, GP5 for left wheel, GP7, GP6 for right wheel) before the order was wrong
actuator = Actuator(3, 2) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)

#-----------------------Set up sensors
distance_sensor=DistanceSensor()
code_reader=QRCodeReader()
sensors=[LineSensor(18),LineSensor(19),LineSensor(20),LineSensor(21)]
button = Button(pin = 14) #push button
crash_sensor = Button(pin = 12)
led = LED(pin = 17)

direction=0
forward_speed=90
rotate_speed=80
forward_distance=2/100 #5cm
rpm_full_load = 40
d_wheel = 6.5/100
D = 19/100

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
def line_following(speed = 90):
    if sensors[2].read() == 1:
        wheels.turn_right(speed)
    elif sensors[1].read() == 1:
        wheels.turn_left(speed)
    else:
        wheels.forward(speed)

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
        time=angle*3.14*0.5/(180*w_ic) #leave some room for adjustment
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
                
def full_rotation(direction,speed=rotate_speed*0.7,angle=180):
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
        #sleep(3)  # Short delay for stability
        wheels.full_rotation(direction=direction,speed=speed) #0 for anticlockwise, 1 for clockwise
        sleep(time)
        if direction == 1:
            while sensors[1].read() != 1:
                wheels.full_rotation(direction = direction, speed=speed)
        if direction == 0:
            while sensors[2].read() != 1:
                wheels.full_rotation(direction = direction, speed = speed)
        
        wheels.stop()
        sleep(0.1)

def navigate(route):
    n_steps = len(route)
    cur_step = 0
    global junction_flag,direction,poll_timer
    junction_flag = 0

    #Set up timer
    tim = Timer()

    #Assign interrupts that set the flag to be 1 if either sensor detects a line
    attach_junction_interrupts()

    #while button.read() == 0:
        #pass

    # while junction_flag == 0:
    #     #First step just run continuous action
    #     route[cur_step][2]()

    while cur_step < n_steps:
        if junction_flag == 1 : 
            print(junction_flag)
            #wheels.stop()
            #sleep(1)
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
                tim.init(period=500, mode=Timer.ONE_SHOT, callback=attach_junction_interrupts)
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
    
def button_reset(pin):
    reset()


def pick_up_block(r = 0, depo = 1,distance_cm=6.8):
    #set r if needs to revers before 180
    #detach_junction_interrupts()
    global junction_flag
    junction_flag =0
    attach_junction_interrupts()
    actuator.retract(speed = 100)
    sleep(4)
    actuator.extend()
    sleep(2.55)
    actuator.stop()
    while True:
        if (data := code_reader.read_qr_code()) is not None:
            print(data)
            break
        elif distance_sensor.read() >= distance_cm:
            line_following(speed = 40)
        else:
            wheels.reverse()
            sleep(1)
    wheels.stop()
    
         
    while distance_sensor.read() >= distance_cm:
        print(distance_sensor.read())
        if junction_flag!=0:
            wheels.forward(speed=50)
            sleep(0.5)
            junction_flag = 0
        else:
            line_following(speed = 50)
    
    wheels.stop()
    
    if r == 1:
        wheels.reverse(speed = 60)
        sleep(0.3)
        wheels.stop()
        
    actuator.retract()
    sleep(3)
    actuator.stop()
    
    if r == 1:
        wheels.reverse()
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

def drop_off(data):
        detach_junction_interrupts()
    #if distance_sensor.read() < distance_cm: #we may not need this
        wheels.forward()
        if data == 'A':
            sleep(0.4)
            wheels.stop()
        else:
            sleep(0.4)
            wheels.stop()
            
        actuator.extend()
        sleep(2.55)
        actuator.stop()
        wheels.reverse()
        sleep(0.55) #need to adjust sleep time
        wheels.stop()
        actuator.retract()
        sleep(3)
        actuator.stop()
        if data == 'D':
            full_rotation(direction = 1)
        else:
            full_rotation(direction = 0)
        attach_junction_interrupts()
        # rotate(direction="left",angle=180)


def main():

    wheels.stop()
    actuator.stop()
    led.stop_flash()
    
    while button.read() == 0:
        pass

    
    actuator.retract(speed = 100)
    sleep(2.5)
    actuator.stop()

    led.start_flash() #starts flashing as soon as starts first route
    
    #attach_button_interrupt()

#this is the actual main structure for the competition
    navigate(routes["D1"][0])
    n=1
    for i in range(n):
        if n == n-1:
            data=pick_up_block(r= 1, depo=1)
        else:
            data=pick_up_block(r = 0, depo=1)
            
        navigate(routes[data][0])
        drop_off(data)
            
        if i<n-1:
            navigate(routes[data][1])
                
        else:
            if data == 'D' or data == 'C':
                navigate(routes['A'][4])
                led.stop_flash()
                wheels.stop()
            else:
                navigate(routes[data][4])
                led.stop_flash()
                wheels.stop()

    for i in range(n):
        data=pick_up_block(depo=2)
        navigate(routes[data][2])
        drop_off(data)
        #sleep(2) 
        if i<n-1:
            navigate(routes[data][2])
        else:
           navigate(routes["D2_to_start"])
           led.stop_flash() #stops flashing as soon as finished last route'''
    
if __name__ == "__main__":
    main()

