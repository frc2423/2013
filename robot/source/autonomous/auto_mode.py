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

#time for velocity
t = 1
distance_1 = 5
distance_2 = 8.81
right_angle = 90
left_angle = -90

class Autonomous(object):
    '''storing each component object
    starts from 4 different positions, moves a certain distance to be able to shoot, then turns and uses autoshooter'''
    
    def __init__(self, my_drive, my_shooter_platform, my_target_detector, my_shooter, my_auto_targeting):
        
        self.driving = my_drive
        self.shooter_platform = my_shooter_platform
        self.target_detector = my_target_detector
        self.shooter = my_shooter
        self.auto_targeting = my_auto_targeting
        
        
    #staring from the bottom left corner of the pyramid facing away from the pyramid and parallel to the goals
    def bottom_left(self):
        self.driving.drive(distance_1/t, 0)
        if self.target_detector.GetData:
            self.auto_targeting
            self.auto_shoot
            
        else:
            self.RobotTurner.set_angle(left_angle)
            self.RobotTurner.auto_turn()
            
    #Place robot at the bottom right corner of the pyramid facing away from the pyramid and parallel to the goals
    def bottom_right(self):
        self.driving.drive(distance_1/t, 0)
        if self.target_detector.GetData:
            self.auto_targeting
            self.auto_shoot
            
        else:
            self.RobotTurner.set_angle(right_angle)
            self.RobotTurner.auto_turn()
            
    #PLace robot at top left corner of the pyramid facing away from the pyramid and parallel to the goals
    def top_left(self):
        self.driving.drive(distance_2/t, 0)
        if self.target_detector.GetData:
            self.auto_targeting
            self.auto_shoot
            
        else:
            self.RobotTurner.set_angle(left_angle)
            self.RobotTurner.auto_turn()
            
    #Place robot at the top right corner of the pyramid facing away from the pyramid and parallel to the goal
    def top_right(self):
        self.driving.drive(distance_2/t, 0)
        if self.target_detector.GetData:
            self.auto_targeting
            self.auto_shoot
            
        else:
            self.RobotTurner.set_angle(right_angle)
            self.RobotTurner.auto_turn()
            
    def update(self, time_elapsed):
        if self.time_elapsed <t:
            self.driving.drive(1, 0)
        else:
            target_data =  self.target_detector.get_data()
            if target_data[0] == None:
                self.driving.drive(0, .5)
            elif not self.target_detector.is_aimed():
                self.auto_targeting.perform_targeting()
            else:
                if self.shooter_platform.wheel_on != True:
                    self.shooter_platform.set_on()
                self.shooter.shoot_if_ready()
                
                
                
                
            
    
        
            
 
        
        
    
        
        
        
        
        
        
        
        
                