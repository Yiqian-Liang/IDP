from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from line_sensor import LineSensor
from machine import Pin, PWM, I2C, Timer
from time import sleep
import routes

wheels = Wheel((4,5),(7,6))
actuator = Actuator(8, 9) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)
#navigation function
# message_string=QRCodeReader.read_qr_code()
# destination=QRCodeReader.parse_qr_data(message_string)
sensors=[LineSensor(12),LineSensor(13),LineSensor(14),LineSensor(15)]

button = Pin(22, Pin.IN, Pin.PULL_DOWN)

def junction_detected(pin):
    global junction_flag
    junction_flag = 1  # Set the flag when an interrupt occurs

def attach_interrupts(timer = None):
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
    junction_flag = 0

    #Set up timer
    tim = Timer()

    #Assign interrupts that set the flag to be 1 if either sensor detects a line
    tim.init(period=500, mode=Timer.ONE_SHOT, callback=attach_interrupts)

    while junction_flag == 0:
        if route[cur_step][2] is None:
            #e.g. if first step is turn right
            pass
        else:
            #First step just run continuous action
            route[cur_step][2]()

    while True:
        #When junction flag == 1
        if junction_flag == 1:
            #increment step (i.e. first step will be 0)
            cur_step += 1
            #Temporarily unnattach interrupts
            sensors[0].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
            sensors[-1].pin.irq(trigger = Pin.IRQ_RISING, handler = None)
            junction_flag = 0

            #Perform safety check on junction if necessary
            if route[cur_step][0] is not None:
                while safety_check(route[cur_step][0]) == 0:
                    #if failed check, maybe reverse?
                    pass
            
            #Carry out turning if necessary
            if route[cur_step][1] is not None :

                route[cur_step][1]()
    
        else:
            if cur_step == n_steps - 1:
                #if it's the last action don't reset the juunction flag
                route[cur_step][2]()
                #The final action in the route should then call the next route
                #This will depend on previous location, number of deliveries etc
            else:
                #Set timer to reattach interrupts once moved away from junction
                #Junction recovery time may need adjusting
                tim.init(period=500, mode=Timer.ONE_SHOT, callback=attach_interrupts)
                while junction_flag != 1:
                    #Perform continuous action until junction detected
                    route[cur_step][2]()




def safety_check(junction):
    #simple check if the junction matches what we expect
    if (sensors[0] == junction [0]) and (sensors[-1] == junction[-1]):
        return 1
    else:
        return 0

def start_robot():
    global package_number
    package_number = 1
    global cur_location
    cur_location = None
    while button.value() == 0:
        pass
    navigate(routes.startd1)

def last_action():
    wheels.stop()
    while button.value() == 0:
        pass
    navigate(routes.d1A)


