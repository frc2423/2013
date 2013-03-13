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
    
    # Set this to True if this is the default autonomous mode, otherwise False
    DEFAULT = False


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
            performs to zero and climbing controls
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
        self.platform.set_angle_auto(0)
        self.platform.set_speed_manual(0.0)
        
        #
        #    Climber
        #        - Must come after anything that sets angle, otherwise
        #        the climbing safety features won't kick in
        #
        
        if self.stick_button_on(self.CLIMB_DOWN_BUTTON):
            self.my_climber.lower()
        elif self.stick_button_on(self.CLIMB_UP_BUTTON):
            self.my_climber.climb() 
        
        #
        #climbing rotation, set after driving to override joystick input
        #
        if self.stick_button_on(self.CLIMB_TWIST_L_BUTTON):
            self.drive.drive(0.0, -0.9)
        elif self.stick_button_on(self.CLIMB_TWIST_R_BUTTON):
            self.drive.drive(0.0, 0.9)
                  
            
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
        