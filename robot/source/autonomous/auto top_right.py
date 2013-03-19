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


class TopRight(object):
    
    MODE_NAME = "top_right"
    DEFAULT = False


    def __init__(self, components):
        
        self.driving = components['drive']
        self.shooter_platform = components ['shooter_platform']
        self.target_detector = components ['target_detector']
        self.shooter = ['shooter']
        self.auto_targeting = ['auto_targeting']
        
        
        
    def on_enable(self):
        #t determined by t = distance/v where distance is either top or bottom and v is the robot's speed
        v = 1
        distance_top = 8.81
        t = distance_top/v
        #replace power of driving appropriately 
        ang_pw_right = .5
        drive_pw = 1
        
        pass
        
        
    def on_disable(self):
        pass
        
    def update(self, time_elapsed):
        v = 1
        distance_top = 8.81
        t = distance_top/v
        ang_pw_right = .5
        drive_pw = 1 
        #needs an is_aimed() function
        if time_elapsed < t:
            self.driving.drive(drive_pw, 0)
            
        #turn until target is retrieved; turn wheel on if off; shoot when ready
        else:
            target_data = self.target_detector.get_data()
            if target_data[0] == None:
                self.driving.drive(0, ang_pw_right)
            elif not self.target_detector.is_aimed():
                self.auto_targeting.perform_targeting()
            else:
                if self.shooter_platform.wheel_on != True:
                    self.shooter_platform.set_on()
                self.shooter.shoot_if_ready()
                
        