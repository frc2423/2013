
from common.conversions import *

from threading import Condition

try:
    import wpilib
except:
    import fake_wpilib as wpilib
    
''' smart dashboard value '''
DASH_STRING = "FRISBEE_SPEED"

''' states '''
NO_FRISBEE = 0
FRISBEE_FUZZY = 1
FRISBEE_MOVING = 2
FRISBEE_SHOT = 3

''' distances in cm (rough guess)'''
FRISBEE_FUZZY_EDGE = 5.5
FRISBEE_EDGE = 5 
FRISBEE_LENGTH = 27

'''other'''
WAIT_TIME = .05

''' settings '''
METRIC = 0
ENGLISH = 1
class FrisbeeSpeed(object):
    ''' 
        Estimates frisbee speed based on how long a frisbee takes to pass and 
        the length of the part of the frisbee that passes by. All distances
        are in cm. To run, run start() on a new thread
    '''
    
    def __init__(self, distance_sensor, system = ENGLISH):
        '''
            initializes FrisbeeSpeed
            Parameters: distance_sensor,  a distance_sensor
        '''
        self.state = NO_FRISBEE
        self.distance_sensor = distance_sensor
        self.timer = wpilib.Timer()
        self.condition = Condition()
        self.system =  system
        ''' I hate the english system '''
    
        self.distance_sensor.system = self.distance_sensor.METRIC
            
    def process_speed(self):
        '''
            Goes through a state machine that informs it when a frisbee passed
            through
        '''
        distance = self.distance_sensor.GetDistance()
        
        if self.state == NO_FRISBEE:
            if distance >= FRISBEE_FUZZY_EDGE:
                self.state = FRISBEE_FUZZY
                self.timer.Start()
                
        if self.state == FRISBEE_FUZZY:
            if distance > FRISBEE_EDGE:
                
                self.state = FRISBEE_MOVING
            
            if distance < FRISBEE_FUZY_EDGE:    
                self.timer.Stop()
                self.timer.Reset()
                self.state = NO_FRISBEE
                
        if self.state == FRISBEE_MOVING:
            if distance < FRISBEE_FUZY_EDGE:
                self.timer.Stop()
                time = self.timer.Get()
                ''' in cm per second'''
                self.speed = FRISBEE_LENGTH / time
                
                if self.system == ENGLISH:
                    self.speed *= CM_TO_FEET
                
                wpilib.SmartDashboard.PutNumber(DASH_STRING, self.speed)
                self.state = NO_FRISBEE


        
    def run(self):
        '''
            Starts processing the speed
        '''
        with self.condition:
            while True:
                
                self.condition.wait()
                
                self.run = True
                
                while self.run:
                    
                    process_speed()
                    wpilib.Wait(WAIT_TIME)
            
                self.state == NO_FRISBEE
        
    def start(self):
        '''
            begins collection of speed info
        '''
        self.condition.notify()
        
    def stop(self):
        '''
            terminates the Frisbee Speed getter thingy
        '''
        self.run = False