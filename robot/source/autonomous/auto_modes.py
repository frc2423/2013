'''We will have 4 Autonomous modes. 
One for each of the 4 starting modes (each corner of the pyramid)'''


try:
    import wpilib 
except ImportError:
    import fake_wpilib as wpilib
    

from components.driving import Driving
from components.shooter_platform import ShooterPlatform
from components.target_detector import TargetDetector

from systems.shooter import Shooter
from systems.auto_targeting import AutoTargeting
from systems.robot_turner import RobotTurner

WHEEL_SPEED = .9

class AutoModes(object):
    
    def __init__(self, components):
        
        self.driving = components['drive']
        self.shooter_platform = components ['shooter_platform']
        self.target_detector = components ['target_detector']
        self.shooter = components['shooter']
        self.auto_targeting = components['auto_targeting']
        self.turner = components['robot_turner']
        # local targeted value
        self.is_targeted = False
        
        # these should be overrided by the respective AutoModes
        self.turn_power = .7
        self.drive_power = 1.0
        self.move_time = 1.5
    def on_enable(self):
        pass
        
        
    def on_disable(self):
        ''' disable shooter, don't want to start with it on'''
        self.shooter_platform.set_speed_manual(0.0)
        
    def update(self, time_elapsed):
        if time_elapsed < self.move_time:
            self.driving.drive(self.drive_power, 0.0)
        #turn until target is retrieved; turn wheel on if off; shoot when ready
        else:
            target_data = self.target_detector.get_data()
            if target_data[0] == None:
                self.driving.drive(0.0, self.turn_power)
            elif not self.auto_targeting.is_aimed() and not self.is_targeted:
                self.auto_targeting.perform_targeting()
                self.turner.auto_turn()
            else:
                #we targeted once, so lets remember that and try to shoot
                self.is_targeted = True
                self.shooter_platform.set_speed_manual(WHEEL_SPEED)
                self.shooter.shoot_if_ready()
                
class TopRight(AutoModes):
    ''' should move 3 - 5 ft turn right and shoot '''
    MODE_NAME = "top_right"
    DEFAULT = True
    
    def __init__(self,components):
        super().__init__(components)
        self.turn_power = -.7
        self.drive_power = 1.0
        self.move_time = 1.5
    
class TopLeft(AutoModes):
    ''' should move 3 - 5 ft turn left and shoot ''' 
    MODE_NAME = "top_left"
    DEFAULT = False
    
    def __init__(self,components):
        super().__init__(components)
        self.turn_power = .7
        self.drive_power = 1.0
        self.move_time = 1.5
        
class BottomRight(AutoModes):
    ''' should move ~ 8 - 9 ft turn right and shoot (might not work)'''
    MODE_NAME = "bottom_right"
    DEFAULT = False
    
    def __init__(self,components):
        super().__init__(components)
        self.turn_power = -.7
        self.drive_power = 1.0
        self.move_time = 3
        
class BottomLeft(AutoModes):
    ''' should move ~ 8 - 9 ft turn left and shoot (might not work)'''
    MODE_NAME = "bottom_left"
    DEFAULT = False
    
    def __init__(self,components):
        super().__init__(components)
        # these should be overrided by the respective AutoModes
        self.turn_power = .7
        self.drive_power = 1.0
        self.move_time = 3
        
class DumbMode(AutoModes):
    '''
        This mode just sets the angle to max and shoots when ready
    '''
    MODE_NAME = "dumb_mode"
    DEFAULT = False
    
    def __init__(self, components):
        super().__init__(components)
        
    def update(self, time_elapsed):
        ''' Assume sensors are broken and override regular update function'''
        
        #raise shooter platform to max 
        while not self.shooter_platform.at_max():
            self.shooter_platform.set_speed_manual(\
                            self.shooter_platform.RAISE_ANGLE_SPEED)
        
        if self.shooter_platform.at_max():
            #shoot if wheel is at ready speed
            self.shooter_platform.set_speed_manual(WHEEL_SPEED)
            self.shooter.shoot_if_ready()    
        