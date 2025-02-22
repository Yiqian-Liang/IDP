from motor import Wheel, Actuator  # Import the Wheel and Actuator classes
from time import sleep
import time
from sensors import QRCodeReader, DistanceSensor, LineSensor, LED, Button #sensors we are using
from machine import Pin, PWM, I2C, Timer
from do_route import speed_and_time, routes, rotate, full_rotation, wheels, attach_junction_interrupts, detach_junction_interrupts, junction_detected
import jf
import random

#---------------------- Set up motors
actuator = Actuator(3, 2) # Initialize linear actuator (GP8 for direction, GP9 for PWM control)

#-----------------------Set up sensors
distance_sensor=DistanceSensor()
code_reader=QRCodeReader()
sensors=[LineSensor(18),LineSensor(19),LineSensor(20),LineSensor(21)]
button = Button(pin = 14) #push button
crash_sensor = Button(pin = 12)
led = LED(pin = 17)

forward_speed=90
actuator_speed=80
extension=14 #14mm
drop_off_distance=10 #10cm
actuator_max_speed=7 #7mm/s

# Simplified line following function
def line_following(speed = 90):
    if sensors[2].read() == 1:
        wheels.turn_right(speed)
    elif sensors[1].read() == 1:
        wheels.turn_left(speed)
    else:
        wheels.forward(speed)

def navigate(route):
    n_steps = len(route)
    cur_step = 0
    jf.junction_flag = 0 #global jf.junction_flag

    #Set up timer
    tim = Timer()

    #Assign interrupts that set the flag to be 1 if either sensor detects a line
    attach_junction_interrupts()
    print(jf.junction_flag)

    while cur_step < n_steps:
        if jf.junction_flag == 1 : 
            print(jf.junction_flag)
            detach_junction_interrupts()
            #detach_polling()
            jf.junction_flag = 0
            if route[cur_step][1] is not None:
                route[cur_step][1]()
                cur_step += 1
                attach_junction_interrupts()
            else:
                line_following()
                tim.init(period=500, mode=Timer.ONE_SHOT, callback=attach_junction_interrupts)
                cur_step += 1
        else:
            line_following()
    wheels.stop()

def extend(speed=actuator_speed): #extend actuator for precise time so that it fits into the block
    time=extension/(actuator_max_speed*speed/100)
    actuator.extend(speed)
    sleep(time)
    actuator.stop()
    return time
def retract(speed=actuator_speed): #retract actuator for certain time
    time=extension/(actuator_max_speed*speed/100)*1.25 #EXTRA FOR SAFETY
    actuator.retract(speed)
    sleep(time)
    actuator.stop()
    return time
    
def pick_up(a, depo=1, speed=80, d_rev=7, d_safe=7.0):
    # Compute wheel speed parameters based on safe distance.
    v_wheel, t_safe = speed_and_time(speed, d_safe)
    
    data1 = None
    data2 = None
    attempt=0
    if a>=1:
        wheels.forward(speed/2)
    extend()

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
            if attempt > 3:    
                # If the robot reaches the safe distance without detecting a QR code,# reverse for a calculated duration and then try again.
                data2=random.choice(['A', 'B', 'C', 'D'])
                break #if we can't read just deliver to random point)
            else:
                _, t_safe = speed_and_time(speed, d_safe+5)
                wheels.reverse(speed)
                sleep(t_safe)
                wheels.stop()
    # Continue with any subsequent actions           
    # Fine adjustment: reverse slowly for a short distance.
    #_, t_adjust = speed_and_time(speed/2, d_safe/5)
    #sleep(t_adjust)
    wheels.reverse(speed/2)
    actuator.retract(speed=100)
    wheels.stop()
    if a > 2:
        _, t_reverse = speed_and_time(speed, (a - 2) * d_rev)
        wheels.reverse(speed)
        sleep(t_reverse)
        wheels.stop()
        sleep(2)
    # Rotate 180° based on depo parameter.
    if depo == 1:
        full_rotation(1)  # Rotate right.
    elif depo == 2:
        full_rotation(0)  # Rotate left.
    actuator.stop()
    return data2

def drop_off(data, depo = 1):
        detach_junction_interrupts()
        if depo == 1 or data == 'D' or data == 'C': #If second time round, sometimes no space for fwd
            wheels.forward()
            sleep(0.4)
        wheels.stop()
            
        actuator.extend()
        sleep(2.55)
        actuator.stop()
        wheels.reverse()#reverse out from the block
        if data == 'D':
            sleep(0.5)
        else:
            sleep(0.55)
        wheels.stop()
        actuator.retract()#retract once far enough back to minimise risk of collision
        sleep(3)
        actuator.stop()
        if data == 'D':#different directions/reversing required for each drop off point
            full_rotation(direction = 1)
            wheels.reverse(speed = 60)
            sleep(0.5)
            wheels.stop()
        elif data == 'C':
            full_rotation(direction = 1)
        elif data == 'B':
            full_rotation(direction = 1)
            wheels.reverse(speed = 60)
            sleep(0.4)
            wheels.stop()
        elif depo == 2 and data == 'Α':
            full_rotation(direction = 0)
            wheels.reverse(speed = 60)
            sleep(0.4)
            wheels.stop()
        else:
            full_rotation(direction = 0)
        attach_junction_interrupts()

def main():
    wheels.stop()
    actuator.stop()
    led.stop_flash()
    
    while button.read() == 0:#wait for button to start
        pass

    start=time.time() #start a timer to keep track of time
    actuator.retract()#retract while moving to ensure all the way up

    led.start_flash() #starts flashing as soon as starts first route
    
#this is the main structure for the competition
    navigate(routes["D1"][0])#go to first depo
    actuator.stop()
    n=4
    for i in range(n):#repeat this for each block
        data=pick_up(a=i, depo=1)           
        navigate(routes[data][0])
        drop_off(data)
            
        if i<n-1: #first 3 times go back to depo 1
            navigate(routes[data][1])                
        else:
            if time.time()-start<240:
                # on 4th time, if time is less than 4 minutes, go to depo 2 for a 5th, final block
                navigate(routes[data][3])
                data = pick_up(depo = 2, a = 0)
                if data != 'B': #couldn't get B working before comp, so just go to A
                    navigate(routes[data][2])
                    drop_off(data = data, depo = 2)
                    navigate(routes[data][4])
                else:
                    navigate(routes['A'][2])
                    drop_off(data = 'A', depo = 2)
                    navigate(routes['A'][4])
            else:
                navigate(routes[data][4])
            wheels.forward()# go forward into the end zone
            sleep(1.8)
            led.stop_flash()
            wheels.stop()

    
if __name__ == "__main__":
    main()







