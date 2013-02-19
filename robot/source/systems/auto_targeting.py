
import sys

class AutoTargeting(object):
    
    def __init__(self, robot_turner, shooter_platform, target_detector):
        self.shooter_platform = shooter_platform
        self.robot_turner = robot_turner
        self.target_detector = target_detector
        
        self.last_hangle = 0.0
        self.last_vangle = 0.0
    
    def perform_targeting(self):
        '''Perform targeting actions'''
        
        # get angle
        hangle, vangle, distance = self.target_detector.get_data()
        
        if hangle is None:
            return
        
        # if an angle has changed, set it
        if abs(vangle - self.last_vangle) > 0.1:
            self.robot_turner.set_angle(vangle)
            self.last_vangle = vangle
            
        if abs(hangle - self.last_hangle) > 0.1:
            current_hangle = self.shooter_platform.current_angle()
            self.last_hangle = current_hangle + hangle
        
        self.shooter_platform.set_angle_auto(self.last_hangle)
        
    # no update function required