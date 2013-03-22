'''
    Author: Sam Rosenblum
    Date:   3/10/2013
    
    Description:
    
        This operator control mode represents a control mode that forces lowering
        of platform but allows climbing. It is used when we are trying to climb
        the pyramid. This mode cannot shoot.
'''

from common.joystick_util import * 

class ClimbingMode(object):

    # this name should be descriptive and unique. This will be shown to the user
    # on the SmartDashboard
    MODE_NAME = "Climbing Mode"
    
    # Set this to True if this is the default mode, otherwise False
    DEFAULT = False


    def __init__(self, components, ds):
        '''
            Constructor
            
            params:components    dictionary of components
            params:ds            driver station instance
        '''
        self.climber = components['climber']
        self.platform = components['shooter_platform']
        self.drive = components['drive']
        self.feeder = components['feeder']
        self.ds = ds
        
    def on_enable(self):
        pass
        
    def on_disable(self):
        pass
    
    def set(self):
        '''
            performs to zero and climbing controls
        '''
        # 
        #    Driving
        #
        ds = self.ds
        self.drive.drive(stick_axis(DRIVE_SPEED_AXIS, ds),
                            stick_axis(DRIVE_ROTATE_AXIS, ds),
                            stick_button_on(DRIVE_FASTER_BUTTON, ds))
        #
        #    Shooter
        #
        self.platform.set_angle_manual(self.platform.LOWER_ANGLE_SPEED)
        self.platform.set_speed_manual(0.0)
        
        #
        #    Climber
        #        - Must come after anything that sets angle, otherwise
        #        the climbing safety features won't kick in
        #
        
        if stick_button_on(CLIMB_DOWN_BUTTON, ds):
            self.climber.lower()
        elif stick_button_on(CLIMB_UP_BUTTON, ds):
            self.climber.climb() 
        
        #
        #climbing rotation, set after driving to override joystick input
        #
        if stick_button_on(CLIMB_TWIST_L_BUTTON, ds):
            self.drive.drive(0.0, -0.9)
        elif stick_button_on(CLIMB_TWIST_R_BUTTON, ds):
            self.drive.drive(0.0, 0.9)

