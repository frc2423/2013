
import math

class RobotTurner(object):
    '''Turn the robot automagically'''
    
    # angle to decay the angle by
    DECAY = 0.5
    SPEED_MAX = 0.7
    
    # sorted list of angle, speed
    # -> don't make too many in this list, since we iterate on it linearly
    THRESHOLDS = [
        (1.0,  0.30),
        (5.0,  0.45),
        (10.0, 0.60),
        (20.0, 0.65),
    ]
    
    def __init__(self, driving):
        self.driving = driving
        self.angle = 0
        
    def set_angle(self, angle):
        '''Only set this when you have new data. This must be called before
           auto_turn. Angle is specified in degrees'''
        self.angle = angle
        
    def auto_turn(self):
        '''This should always be called when you want the turn to happen'''
        
        a = abs(self.angle)
        rotate = self.SPEED_MAX
        
        # too lazy to do math here... :)
        for ta, tr in self.THRESHOLDS:
            if a <= ta:
                rotate = tr
                break
        
        self.driving.drive(0, math.copysign(rotate, self.angle))
        
        
    def update(self):
        
        # decay the angle by some N
        # -> Really, this should be on a thread. But we've had problems with
        #    threads on the cRio, so do this for now
        if self.angle != 0:
            if self.angle < 0:
                self.angle += self.DECAY
                if self.angle > 0:
                    self.angle = 0   # done turning 
            else:
                self.angle -= self.DECAY
                if self.angle < 0:
                    self.angle = 0   # done turning
        
        