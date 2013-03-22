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

class AutoModes(object):
    
    def __init__(self, components):
        
        self.driving = components['drive']
        self.feeder = components['feeder']
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
                self.shooter_platform.set_speed_manual(self.shooter_platform.WHEEL_SPEED_ON)
                self.shooter.shoot_if_ready()
                
class TopRight(AutoModes):
    ''' should move 3 - 5 ft turn right and shoot '''
    MODE_NAME = "top_right"
    DEFAULT = False
    
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
    DEFAULT = True
    
    def __init__(self, components):
        super().__init__(components)
        
    def on_enable(self):
        self.empty = False
        self.at_max = False
        self.start = 0
        
    def update(self, time_elapsed):
        ''' Assume sensors are broken and override regular update function'''
        
        # turn the wheel on
        if not self.empty:
            self.shooter_platform.set_speed_manual(self.shooter_platform.WHEEL_SPEED_ON)
        
        #raise shooter platform to max 
        if not self.at_max:
            
            self.shooter_platform.set_angle_manual(self.shooter_platform.RAISE_ANGLE_SPEED)
            if self.shooter_platform.at_max():
                self.at_max = True
                self.start = time_elapsed
        else:
            diff = time_elapsed - self.start
            
            # feed 3 times, once every 2 seconds
            if diff > 0 and diff < .25:
                self.feeder.feed_auto()
                
            elif diff > 2 and diff < 2.25:
                self.feeder.feed_auto()
                
            elif diff > 4 and diff < 4.25:
                self.feeder.feed_auto()
                
            elif diff > 5:
                self.empty = True
