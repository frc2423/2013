'''
    Author: Sam Rosenblum
    Date:   3/10/2013
    
    Description:
    
        Manual control of angle of platform, this is used in the case that the 
        potentiometer breaks and we need to manually compensate for that. Climbing
        is disabled to avoid breaking of platform/climber. This mode can shoot
'''
from common.joystick_util import * 

class ManualMode(object):

    # this name should be descriptive and unique. This will be shown to the user
    # on the SmartDashboard
    MODE_NAME = "Manual Mode"
    
    # Set this to True if this is the default mode, otherwise False
    DEFAULT = True


    def __init__(self, components ,ds):
        '''
            Constructor
            
            params:components    dictionary of components
            params:ds            driver station instance
        '''
        self.climber = components['climber']
        self.shooter_platform = components['shooter_platform']
        self.feeder = components['feeder']
        self.drive = components['drive']
        self.platform = components['shooter_platform']
        self.ds = ds
        
        self.sd = wpilib.SmartDashboard
        
    def on_enable(self):
        # no unexpected firing should occur when switching modes
        self.sd.PutBoolean("Fire", False)
        self.sd.PutNumber("TestAngle", 0)
        
    def on_disable(self):
        '''
            This function is called when Operator Control mode is exiting. You should
            clean anything up here that needs to be cleaned up
        '''
        pass


    def set(self):
        '''
            sets shooter_platform position, lowers climber 
        '''
        # 
        #    Driving
        #
        ds = self.ds
        self.drive.drive(stick_axis(DRIVE_SPEED_AXIS,ds),
                            stick_axis(DRIVE_ROTATE_AXIS,ds),
                            stick_button_on(DRIVE_FASTER_BUTTON,ds))
        
        #
        #    Shooter
        #
        
        if self.sd.GetBoolean("Wheel On"):
            self.platform.set_speed_manual(self.platform.WHEEL_SPEED_ON)
       
        
        #
        # Shooting Platform control
        #
        if stick_button_on(TEST_BUTTON, ds):
            self.shooter_platform.set_angle_auto(self.sd.GetBoolean("TestAngle"))
        else:
            self.shooter_platform.set_angle_manual(-stick_axis(PLATFORM_ANGLE_AXIS, ds))
        
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
        # climbing rotation, set after driving to override joystick input
        #
        if stick_button_on(CLIMB_TWIST_L_BUTTON, ds):
            self.drive.drive(0.0, -0.9)
        elif stick_button_on(CLIMB_TWIST_R_BUTTON, ds):
            self.drive.drive(0.0, 0.9)
        
        #
        #    Feeder
        #
        #    
        fire_counter = self.sd.GetBoolean("Fire")
        if stick_button_on(FEEDER_FEED_BUTTON, ds) or fire_counter == True:
            self.sd.PutBoolean("Fire", False)
            self.feeder.feed()
        elif stick_button_on(FEEDER_BACK_BUTTON, ds):
            self.feeder.reverse_feed()

 
