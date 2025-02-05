from main import line_following, rotate_180, rotate_left, rotate_right, pickup, drop_off
from motor import Wheel
from navigate_joseph import navigate, last_action
wheels = Wheel((4,5),(7,6))

#route from start box to depot 1
route_startd1 = [[None, None, wheels.forward], 
                 [None, None, line_following],
                 [None, rotate_right, line_following],
                 [None, rotate_right, pickup]]
#route from depot 1 to A
route_d1A = [[None, None, line_following],
             [None, rotate_180, line_following], 
             [None, rotate_left, line_following], 
             [None, None, line_following],
             [None, rotate_right, line_following],
             [None, None, drop_off]]
#route from depot 1 to B
route_d1B = [[None, None, line_following],
             [None, rotate_left, line_following],
             [None, rotate_left, drop_off]]
#route from A to depot 1
route_Ad1 = [[None,None,line_following], 
             [None, rotate_180, line_following],
             [None, rotate_left, line_following],
             [None,None,line_following],
             [None, rotate_right, wheels.stop]]

navigate(route_d1A)