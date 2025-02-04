from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from line_sensor import LineSensor
from distance_sensor import DistanceSensor
from threading import Timer #To create timer interrupts
from main import rotate_left, rotate_right, line_following #to test the route
from machine import Pin, PWM, I2C
distance_sensor=DistanceSensor()
code_reader=QRCodeReader()
wheels = Wheel((7,6), (4, 5))
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

def line_following_rev():
    line_following(direction = 1) #so I don't need to put in arguments when run

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
    junction_flag = 0

    #Assign interrupts that set the flag to be 1 if either sensor detects a line
    attach_interrupts()

    #First action, only do the continuous action
    while junction_flag == 0:
        route[0][2]()

    while True:
        #When junction flag == 1
        if junction_flag == 1:
            cur_step += 1
            #Perform safety check on junction if necessary
            if route[cur_step][0] is not None:
                while safety_check(route[cur_step][0]) == 0:
                    #if failed check, maybe reverse?
                    pass
            
            #Carry out turning if necessary
            elif route[cur_step][1] is not None :

                route[cur_step][1]()

                #Temporarily unnattach interrupts
                sensors[0].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
                sensors[-1].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
                junction_flag = 0

                #Set timer to reattach interrupts once moved away from junction
                #Junction recovery time may need adjusting
                Timer(0.5, attach_interrupts)
            elif route[cur_step][1] is None:
                Wheel.forward(90)
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

test_route_d1A = [[None, None, line_following_rev], [None, rotate_right, line_following], [None, None, line_following],[None, rotate_right, line_following]]

navigate(test_route_d1A)

