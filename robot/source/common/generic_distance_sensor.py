'''
    Author: Sam Rosenblum
    Date:   2/11/2013
    Updated: 2/5/2013
    
    This file holds the class GenericDistanceSensor which holds with in it
    equations that holds a map that represent best fit equations for different 
    types of distance sensors
'''

import math
import sys


from inspect import currentframe, getframeinfo
from common.conversions import *

try:
    import wpilib
except:
    import fake_wpilib as wpilib

# sensors
GP2D120 = 0

# settings
METRIC = 0
ENGLISH = 1


def lineno():
    #returns current line
    return currentframe().f_back.f_lineno

def get_file_name():
    #returns current file
    return getframeinfo(currentframe()).filename

class GenericDistanceSensor(wpilib.AnalogChannel):

    #sensor_dict hold the map of sensor type to distance equations
    sensor_dict = {0: lambda v: math.pow((v/11.036), -1/.947)}
    
    def __init__(self, channel, sensor_type, system = ENGLISH): 
        '''
            constructor takes a channel and a sensor_type to figure out the
            real distance
        '''
        
        super().__init__(channel)
        self.sensor_type = sensor_type
        self.system = system
        
    def GetDistance(self):
        '''gets distance based on the voltage''' 
        v = self.GetVoltage()
        
        if v != 0:
            
            if self.sensor_type in self.sensor_dict:
                
                distance = self.sensor_dict[self.sensor_type](v)
                
                # convert from metric
                if self.system == ENGLISH:
                    
                    distance /= INCH_TO_CM
                    
                return distance
            
            else:
                
                raise KeyError("The sensor type not found")
        else:
            '''can't divide by zero but prevent crash, the sensor may have malfunctioned'''
            # TODO: What to do with this?
            #sys.stderr.write( "ERROR: Cannot divide by Zero File: %s line number: %s"\
            #                  % (get_file_name(), lineno()) )
            return 0
        
    def GetAverageDistance(self):
        '''gets average distance based on average voltage'''
        
        v = self.GetAverageVoltage()
        
        if v != 0:
            if self.sensor_type in self.sensor_dict:
            
                distance = self.sensor_dict[self.sensor_type](v)

                # convert from metric                
                if self.system == ENGLISH:
                    
                    distance /= INCH_TO_CM
                
                return distance
            
            else:
                
                raise KeyError("The sensor type not found")
        else:
            # can't divide by zero but prevent crash, the sensor may have malfunctioned
            # TODO: What to do with this?
            #sys.stderr.write( "ERROR: Cannot divide by Zero File: %s line number: %s"\
            #                  % (get_file_name(), lineno()) )
            return 0
