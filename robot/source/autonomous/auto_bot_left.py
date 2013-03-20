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

class BottomLeft(object):
    
    MODE_NAME = "bottom_left"
    DEFAULT = False


    def __init__(self, components):
        
        self.driving = components['drive']
        self.shooter_platform = components ['shooter_platform']
        self.target_detector = components ['target_detector']
        self.shooter = ['shooter']
        self.auto_targeting = ['auto_targeting']
        self.turner = ['robot_turner']
        # local targeted value
        self.is_targeted = False        
        
        
    def on_enable(self):
        #t determined by t = distance/v where distance is either top or bottom and v is the robot's speed
        v = 1
        distance_bot = 5
        t = distance_bot/v
        #replace power of driving appropriately 
        ang_pw_left = -.5
        drive_pw = 1
        pass
        
        
    def on_disable(self):
        ''' disable shooter, don't want to start with it on'''
        self.shooter_platform.set_speed_manual(0)
        
    def update(self, time_elapsed):
        v = 1
        distance_bot = 5
        t = distance_bot/v
        ang_pw_left = -.5
        drive_pw = 1
        #needs an is_aimed() function
        if time_elapsed < t:
            self.driving.drive(drive_pw, 0)
            
        #turn until target is retrieved; turn wheel on if off; shoot when ready
        else:
            target_data =  self.target_detector.get_data()
            if target_data[0] == None:
                self.driving.drive(0, ang_pw_left)
            elif not self.auto_targeting.is_aimed() and not self.is_targeted:
                self.auto_targeting.perform_targeting()
            else:
                #we targeted once, so lets remember that and try to shoot
                self.is_targeted = True
                if self.shooter_platform.wheel_on != True:
                    self.shooter_platform.set_speed_manual(WHEEL_SPEED)
                self.shooter.shoot_if_ready()
                
        