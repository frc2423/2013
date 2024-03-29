'''
    Author: Sam Rosenblum
    Date:   3/10/2013
    
    Description:
    
        This operator control mode represents a control mode that forces lowering
        of platform setting angle to 0 degrees and keeps the climber in 
        'lowered' position. It is used when we are trying to load the robot.
        This mode cannot shoot.
'''
from common.joystick_util import * 

class LoadingMode(object):

    # this name should be descriptive and unique. This will be shown to the user
    # on the SmartDashboard
    MODE_NAME = "Loading Mode"
    
    # Since we expect autonomous to shoot out all our frisbees this should be the 
    # default mode 
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
        
        #
        # set climber to lowered
        #
        
        self.climber.lower()
        
    def on_disable(self):
        pass
    
    
    def set(self):
        '''
            set platform to zero and climber to lowered
        '''
        # 
        #    Driving
        #
        ds = self.ds
        self.drive.drive(stick_axis(DRIVE_SPEED_AXIS, ds),
                            stick_axis(DRIVE_ROTATE_AXIS, ds),
                            stick_button_on(DRIVE_FASTER_BUTTON, ds))
        #
        #    Shooter set to 0
        #
        #self.platform.set_angle_auto(0)
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
