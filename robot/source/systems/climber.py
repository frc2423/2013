
class ClimberSystem(object):
    
    def __init__(self, climber, shooter_platform):
        self.climber = climber
        self.shooter_platform = shooter_platform
        
    def climb(self):
        '''Call this to cause the robot to climb'''
        if self.shooter_platform.at_zero():
            self.climber.climb()
        else:
            self.shooter_platform.set_angle_manual(self.shooter_platform.LOWER_ANGLE_SPEED)
    
    def lower(self):
        '''Call this to lower the robot down to the ground'''
        self.climber.lower()
    
    def position(self):
        '''This returns the current climber position'''
        return self.climber.position()
    
    # no update function required

        