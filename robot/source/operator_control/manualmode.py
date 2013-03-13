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
    
    # Set this to True if this is the default autonomous mode, otherwise False
    DEFAULT = False


    def __init__(self, components):
        '''Constructor: store components locally here'''
        self.climber = components['climber']
        self.shooter_platform = components['shooter_platform']
        self.feeder = components['feeder']
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
            sets shooter_platform position, lowers climber 
        '''
        # 
        #    Driving
        #
        
        self.drive.drive(self.stick_axis(self.DRIVE_SPEED_AXIS),
                            self.stick_axis(self.DRIVE_ROTATE_AXIS),
                            self.stick_button_on(self.DRIVE_FASTER_BUTTON))
        
        #
        #    Shooter
        #
        
        shootery = self.translate_axis(self.SHOOTER_WHEEL_AXIS, -1.0, 0.0)
        wpilib.SmartDashboard.PutNumber('Shooter Raw', shootery)
            
        self.platform.set_speed_manual(shootery)
       
        #
        #There should be some sort of toggle for this to turn the shooter on or off
        # 
        # else:
        #     self.my_shooter_platform.set_speed_manual(0.0)   
        
        #
        #Shooting Platform control
        #
        self.shooter_platform.set_angle_manual(-self.stick_axis(self.PLATFORM_ANGLE_AXIS))
        
        #
        #lower climber
        #
        self.climber.lower()
        
        #
        #    Feeder
        #
        #    what happens when the sensor breaks?
        if self.stick_button_on(self.FEEDER_FEED_BUTTON):
            self.feeder.feed_auto()
        elif self.stick_button_on(self.FEEDER_BACK_BUTTON):
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
        
 
