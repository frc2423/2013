

try:
    import wpilib
except ImportError: 
    import fake_wpilib as wpilib

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
        
        wpilib.SmartDashboard.PutBoolean('Auto on', True if hangle is not None else False)
        
        if hangle is None:
            return
        
        # if an angle has changed, set it
        if abs(hangle - self.last_hangle) > 0.1:
            print('got hangle', hangle)
            self.robot_turner.set_angle(hangle)
            self.last_hangle = hangle
            
        if abs(vangle - self.last_vangle) > 0.1:
            current_vangle = self.shooter_platform.current_angle()
            self.last_vangle = current_vangle + vangle
        
        self.shooter_platform.set_angle_auto(self.last_vangle)
        
    # no update function required