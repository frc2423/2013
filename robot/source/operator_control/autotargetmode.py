'''
    Author: Sam Rosenblum
    Date:   3/10/2013
    
    Description:
    
        This operator control mode represents a control mode with AutoTageting control
        of the angle. Angle of the shooter is controlled via the joysticks, the
        climber is permanently set to lower (hooks are up). It is used when we shoot
        automatically. This mode can shoot.
'''
from common.joystick_util import * 

class AutoTargetMode(object):

    # this name should be descriptive and unique. This will be shown to the user
    # on the SmartDashboard
    MODE_NAME = "Auto Target Mode"
    
    # Set this to True if this is the default autonomous mode, otherwise False
    DEFAULT = False


    def __init__(self, components, ds):
        '''
            Constructor
            
            params:components    dictionary of components
            params:ds            driver station instance
        '''
        self.climber = components['climber']
        self.auto_targeting = components['auto_targeting']
        self.robot_turner = components['robot_turner']
        self.feeder = components['feeder']
        self.drive = components['drive']
        self.platform = components['shooter_platform']
        self.ds = ds
        
        self.sd = wpilib.SmartDashboard
    
    def on_enable(self):
        # no unexpected firing should occur when switching modes
        self.sd.PutNumber("Fire", 0)
        
    def on_disable(self):
        '''
            This function is called when Operator Control mode is exiting. You should
            clean anything up here that needs to be cleaned up
        '''
        pass


    def set(self):
        '''
            performs auto targeting and keeps climber constantly in lowered 
            position
        '''
        
        ds = self.ds
        
        #
        #    Shooter
        #
        #    Shooter is manual because we do not have an encoder
        
        if self.sd.GetBoolean("Wheel On"):
            self.platform.set_speed_manual(self.platform.WHEEL_SPEED_ON)
            
        #
        #    set auto targeting of shooter platform and robot position
        #
        self.auto_targeting.perform_targeting()
        
        if stick_button_on(AUTO_TARGET_BUTTON,ds):
            self.robot_turner.auto_turn()
             
    
        # 
        #    Driving
        #
        
        self.drive.drive(stick_axis(DRIVE_SPEED_AXIS, ds),
                            stick_axis(DRIVE_ROTATE_AXIS, ds),
                            stick_button_on(DRIVE_FASTER_BUTTON, ds))

        #
        #    make sure sure climber is lowered 
        #       
        self.climber.lower()
        
        #
        #    Feeder
        #
        
        fire_counter = int(self.sd.GetNumber("Fire"))
        if stick_button_on(FEEDER_FEED_BUTTON, ds) or fire_counter != 0:
            if fire_counter > 0:
                self.sd.PutNumber("Fire", fire_counter - 1)
            self.feeder.feed()
        elif stick_button_on(FEEDER_BACK_BUTTON, ds):
            self.feeder.reverse_feed()
