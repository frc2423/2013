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
    DEFAULT = True


    def __init__(self, components):
        '''Constructor: store components locally here'''
        self.climber = components['climber']
        self.platform = components['shooter_platform']
        self.drive = components['drive']
        self.feeder = components['feeder']
    def on_enable(self):
        pass
        
    def on_disable(self):
        pass
    
    
    def set(self):
        '''
            set platform to zero and climber to lowered
        '''
        # 
        #    Driving
        #
        
        self.drive.drive(self.stick_axis(self.DRIVE_SPEED_AXIS),
                            self.stick_axis(self.DRIVE_ROTATE_AXIS),
                            self.stick_button_on(self.DRIVE_FASTER_BUTTON))
        #
        #    Shooter set to 0
        #
        self.platform.set_angle_auto(0)
        self.platform.set_speed_manual(0.0)
        
        #
        #set climber to lowered
        #
        self.climber.lower()
            
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
        
        