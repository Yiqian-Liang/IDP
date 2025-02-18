from motor import Wheel
from sensors import QRCodeReader, DistanceSensor, LineSensor, LED, Button
from machine import Pin, PWM, I2C, Timer
from time import sleep 
import jf

wheels = Wheel((7,6),(4,5))

sensors=[LineSensor(18),LineSensor(19),LineSensor(20),LineSensor(21)]

d_wheel=6.5/100 #in meters
D=0.19 #in meters ditance between the wheels
direction=0
forward_speed=90
rotate_speed=90
forward_distance=2/100 #5cm
reverse_speed=40
rpm_full_load=40 #rpm=speed*rpm_full_load/100

def speed_and_time(speed,distance_cm=6):
    rpm=speed*rpm_full_load/100
    w_wheel=rpm*2*3.14/60
    v_wheel=d_wheel*w_wheel/2
    time=distance_cm/(v_wheel*100)
    return v_wheel,time

def attach_junction_interrupts(timer = None):
    sensors[0].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)
    sensors[-1].pin.irq(trigger=Pin.IRQ_RISING, handler=junction_detected)
def detach_junction_interrupts():
    sensors[0].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
    sensors[-1].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
def junction_detected(pin):
    #global jf.junction_flag
    jf.junction_flag = 1  # Set the flag when an interrupt occurs

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
                
def full_rotation(direction,speed=rotate_speed*0.8,angle=180):
    # status=sensor_status()
    # Detect a junction (both left and right sensors detect the line)
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
        
# Use dict: 
# - The first list is from D1 to the destination.
# - The second list is from the destination to D1.
# - The third list is from D2 to the destination.
# - The fourth list is from the destination to D2, and so on.
        
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
            [(1, 1), None]
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
            [(1, 1), None]
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
            [(1, 1), None]
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
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 1), lambda: rotate(direction="right")],
            [(0, 1), None],
            [(0, 1), None],
            [(0, 1), lambda: rotate(direction="left")],
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
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), None],
            [(1, 0), lambda: rotate(direction="right")],
            [(0, 1), lambda: rotate(direction="left")],
            [(1, 1), None]
        ],
        [  # C to D1
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 1), lambda: rotate(direction="left")],
            [(0, 1), None],
            [(1, 0), lambda: rotate(direction="right")],
            [(0, 1), None]
        ],
        [  # D2 to C
            [(0, 1), None],
            [(0, 1), lambda: rotate(direction="right")],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), lambda: rotate(direction="left")],
        ],
        [  # C to D2
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 1), lambda: rotate(direction="left")],
            [(0, 1), None],
        ],
        [  # C to start
            [(1, 1), lambda: rotate(direction="right")],
            [(1, 1), lambda: rotate(direction="left")],
            [(0, 1), None],
            [(1, 0), lambda: rotate(direction="right")],
            [(1, 0), lambda: rotate(direction="right")],
            [(1, 0), lambda: rotate(direction="left")]
        ]
    ],
    "D":
    [
        [  # D1 to D
            [(1, 0), None],
            [(1, 0), None],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 1), None]
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
            [(1, 1), None]
        ],
        [  # D to D2
            [(1, 1), lambda: rotate(direction="left")],
            [(1, 0), None],
            [(1, 0), lambda: rotate(direction="left")],
            [(1, 0), None],
            [(1, 0), None],
            #[(0, 0), wheels.stop]
        ],
        [  # D to D1
            [(1, 1), lambda: rotate(direction="right")],
            [(0, 1), lambda: rotate(direction="right")],
            [(0, 1), None],
            [(0, 1), lambda: rotate(direction="right")],
            [(0, 1), lambda: rotate(direction="left")]
        ]
    ]
}




