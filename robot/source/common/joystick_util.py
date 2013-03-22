'''
    Joystick util functions and constants, there is no need to create the overhead
    of an object here
'''
try:
    import wpilib
except ImportError: 
    import fake_wpilib as wpilib
# axis constants
X = wpilib.Joystick.kDefaultXAxis
Y = wpilib.Joystick.kDefaultYAxis
Z = wpilib.Joystick.kDefaultZAxis

# button constants
TRIGGER = wpilib.Joystick.kDefaultTriggerButton      # 1
TOP = wpilib.Joystick.kDefaultTopButton              # 2

#
# Controls configuration
#

# axis definitions -- a tuple of (stick number, axis)
# -> call stick_axis() with this value to get the axis
DRIVE_SPEED_AXIS    = (1, Y)
DRIVE_ROTATE_AXIS   = (1, X)
ANGLE_POINT_AXIS    = (1, Z)

SHOOTER_WHEEL_AXIS  = (2, Z)
PLATFORM_ANGLE_AXIS = (2, Y)

# button definitions -- (stick number, button number)
# -> call stick_button_on() with this value to get True/False

DRIVE_FASTER_BUTTON     = (1, TOP)

CLIMB_TWIST_L_BUTTON    = (1, 8)
CLIMB_TWIST_R_BUTTON    = (1, 9)

CLIMB_UP_BUTTON         = (2, 10)
CLIMB_DOWN_BUTTON       = (2, 11)

FEEDER_FEED_BUTTON      = (2, TRIGGER)
FEEDER_BACK_BUTTON      = (2, TOP)

AUTO_TARGET_BUTTON      = (1, TRIGGER)

TEST_BUTTON             = (1, 6)

#
#    Joystick utility functions (yay overhead!)
#

def stick_axis(cfg, ds):
    return ds.GetStickAxis(*cfg)

def translate_axis(cfg, amin, amax, ds):
    '''Returns an axis value between a min and a max'''
    a = ds.GetStickAxis(*cfg)
    
    # Xmax - (Ymax - Y)( (Xmax - Xmin) / (Ymax - Ymin) )
    return amax - ((1 - a)*( (amax - amin) / 2.0 ) )
    
def stick_button_on(cfg, ds):
    return ds.GetStickButtons( cfg[0] ) & (1 << (cfg[1]-1))