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
    def on_enable(self):
        pass
        
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
        #
        #    Shooter
        #
        #    Shooter is manual because we do not have an encoder
        ds = self.ds
        shootery = translate_axis(SHOOTER_WHEEL_AXIS, -1.0, 0.0, ds)
        wpilib.SmartDashboard.PutNumber('Shooter Raw', shootery)
            
        self.platform.set_speed(shootery)
       
        #
        #There should be some sort of toggle for this to turn the shooter on or off
        # 
        # else:
        #     self.my_shooter_platform.set_speed_manual(0.0)   
            
            
        #
        #    set auto targeting of shooter platform and robot position
        #
        self.auto_targeting.perform_targeting()
        
        if stick_button_on(AUTO_TARGET_BUTTON,ds):
            robot_turner.auto_turn()
             
    
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
        #    what happens when the sensor breaks?
        if stick_button_on(FEEDER_FEED_BUTTON, ds):
            self.feeder.feed()
        elif stick_button_on(FEEDER_BACK_BUTTON, ds):
            self.feeder.reverse_feed()
            
  #  def update(self):
  #      '''
  #          Updates components
  #      '''
  #      #
  #      #update components
  #      #
  #      self.drive.update()
  #      self.climber.update()
  #      self.auto_targeting.update()
  #      self.feeder.update()
        
