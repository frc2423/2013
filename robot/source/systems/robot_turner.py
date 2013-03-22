
try:
    import wpilib
except ImportError: 
    import fake_wpilib as wpilib

import math

class RobotTurner(object):
    '''Turn the robot automagically'''
    
    # angle to decay the angle by
    DECAY = 1.0
    SPEED_MAX = 1.0
    
    # sorted list of angle, speed
    # -> don't make too many in this list, since we iterate on it linearly
    THRESHOLDS = [
        (0.0, 0.0),     #(0.0,  0.0),
        (1.0, .94),    #(1.0,  0.94),
        (5.0, .96),    #(5.0,  0.96),
        (10.0, .985),  #(10.0, 0.985),
        (20.0, 1.0),    #(20.0, 1.0),
    ]
    
    def __init__(self, driving):
        self.driving = driving
        self.angle = 0
        self.updated = False
        
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
        
        #print('angle', self.angle, 'rotate', rotate)
        self.updated = True
        self.driving.drive(0.0, -math.copysign(rotate, self.angle))
        
        
    def update(self):
        
        # decay the angle by some N
        # -> Really, this should be on a thread. But we've had problems with
        #    threads on the cRio, so do this for now
        
        #wpilib.SmartDashboard.PutNumber('Turner Angle', self.angle)
        
        if self.updated == True and self.angle != 0:
            if self.angle < 0.0:
                #print('decay +', self.angle)
                self.angle += self.DECAY
                if self.angle > 0.0:
                    self.angle = 0   # done turning 
            else:
                #print('decay -', self.angle)
                self.angle -= self.DECAY
                if self.angle < 0.0:
                    self.angle = 0   # done turning
                    
        self.updated = False
        
        