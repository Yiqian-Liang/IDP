from main import line_following, rotate_left, rotate_right, pickup, drop_off
#route from start box to depot 1
startd1 = [[None, None, line_following], 
            [None, None, line_following],
            [None, rotate_right, line_following],
            [None, rotate_right, pickup]]
#route from depot 1 to A
d1A = [[None, None, line_following], 
        [None, rotate_left, line_following], 
        [None, None, line_following],
        [None, rotate_right, drop_off]]
#route from depot 1 to B
d1B = [[None, None, line_following],
       [None, None, line_following],
        [None, rotate_left, line_following],
        [None, rotate_left, drop_off]]
#route from depot 1 to C
d1C = [[None, None, line_following],
       [None, None, line_following],
        [None, rotate_left, line_following],
        [None, None, line_following],
        [None, rotate_right, line_following],
        [None, rotate_left, drop_off]]
#route from depot 1 to D
d1D = [[None, None, line_following],
       [None, None, line_following],
        [None, rotate_left, line_following],
        [None, rotate_left, drop_off]]
#route from A to depot 1
Ad1 = [[None,None, line_following],
        [None, rotate_left, line_following],
        [None,None,line_following],
        [None, rotate_right, pickup]]
#route from B to depot 1
Bd1 = [[None, None, line_following],
        [None, rotate_right, line_following],
        [None, rotate_right, line_following],
        [None, None, pickup]]
#route from C to depot 1
Cd1 = [[None, None, line_following],
       [None, rotate_right, line_following],
       [None, rotate_left, line_following],
       [None, None, line_following],
       [None, rotate_right, line_following],
       [None, None, pickup]]
#route from D to depot 1
Dd1 = [[None, None, line_following],
       [None, rotate_right, line_following],
       [None, rotate_right, line_following],
       [None, None, line_following],
       [None, None, pickup]]


