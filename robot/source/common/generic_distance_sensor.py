'''
    Author:  Sam Rosenblum
    Date:    2/11/2013
    Updated: 2/25/2013
    
    This file holds the class GenericDistanceSensor which holds with in it
    equations that holds a map that represent best fit equations for different 
    types of distance sensors
'''

import math
from common.constants import *

try:
    import wpilib
except:
    import fake_wpilib as wpilib

# sensors
GP2D120 = 0

# settings
METRIC = 0
ENGLISH = 1


class GenericDistanceSensor(wpilib.AnalogChannel):

    # For each sensor type, define a function that translates the voltage 
    # to a distance (in metric units)
    SENSOR_EQUATIONS = {
        GP2D120: lambda v: math.pow((v/11.036), -1/.947),
    }
    
    def __init__(self, channel, sensor_type, system=ENGLISH): 
        '''
            constructor takes a channel and a sensor_type to figure out the
            real distance
            
            :param channel: The channel number for the associated analog sensor
        '''
        
        super().__init__(channel)
        
        self.distance_fn = self.SENSOR_EQUATIONS[sensor_type]
        self.system = system
    
        
    def GetDistance(self):
        '''gets distance based on the voltage''' 
        
        v = self.GetVoltage()
        
        # if the value is zero, return zero
        if v <= 0:
            return 0
    
        # convert the voltage to a distance
        distance = self.distance_fn(v)
        
        # convert to appropriate units
        if self.system == ENGLISH:
            distance /= INCH_TO_CM
        
        return distance
      
        
    def GetAverageDistance(self):
        '''Gets average distance based on average voltage'''
        
        v = self.GetAverageVoltage()
                
        # if the value is zero, return zero
        if v <= 0:
            return 0
    
        # convert the voltage to a distance
        distance = self.distance_fn(v)
        
        # convert to appropriate units
        if self.system == ENGLISH:
            distance /= INCH_TO_CM
        
        return distance
