'''
    This is a unit test of driving.py. It is designed to test both expected 
    functionality as well as if code is written correctly. If naming
    conventions are not followed this will break the test. If functionality
    is incorrect this test will print out failure
'''

# directory of component to test
robot_path = '../../robot/source/'
import_robot = False

import sys
import os.path

# make importing _unittest_util possible
sys.path.append(os.path.dirname(__file__))
import _unittest_util

import fake_wpilib as wpilib
import random

class Test(object):
    
    def __init__(self):
        from components import feeder
        
        self.feeder_motor = wpilib.CANJaguar(1)
        self.frisbee_sensor = Test_Sensor(1)
        self.feed_sensor = Test_Sensor(2)
        self.tested_feeder = feeder.Feeder(self.feeder_motor,self.frisbee_sensor, self.feed_sensor)
        
        _unittest_util.validate_docstrings(self.tested_feeder)
        
    def test_get_frisbee_count(self):
        from components import feeder
        self.frisbee_sensor.distance = 0
        if not hasattr(self.tested_feeder, "get_frisbee_count"):
            raise Exception("Please use proper naming conventions")
            
        if self.tested_feeder.get_frisbee_count() != 0:
            raise Exception("Wrong Frisbee Count")
        
        self.frisbee_sensor.distance = random.uniform(0, feeder.ONE_FRISBEE)
        
        if self.tested_feeder.get_frisbee_count() != 0:
            raise Exception("Wrong Frisbee Count (expected 0; distance: %s)" % self.frisbee_sensor.distance)
        
        self.frisbee_sensor.distance = random.uniform(feeder.ONE_FRISBEE, feeder.TWO_FRISBEE)
        
        if self.tested_feeder.get_frisbee_count() != 1:
            raise Exception("Wrong Frisbee Count (expected 1; distance: %s)" % self.frisbee_sensor.distance)
        
        self.frisbee_sensor.distance = random.uniform(feeder.TWO_FRISBEE, feeder.THREE_FRISBEE)
        
        if self.tested_feeder.get_frisbee_count() != 2:
            raise Exception("Wrong Frisbee Count (expected 2; distance: %s)" % self.frisbee_sensor.distance)
        
        self.frisbee_sensor.distance = random.uniform(feeder.THREE_FRISBEE, feeder.FOUR_FRISBEE)
        
        if self.tested_feeder.get_frisbee_count() != 3:
            raise Exception("Wrong Frisbee Count (expected 3; distance: %s)" % self.frisbee_sensor.distance)
        
        self.frisbee_sensor.distance = random.uniform(feeder.FOUR_FRISBEE, 5)
        
        if self.tested_feeder.get_frisbee_count() != 4:
            raise Exception("Wrong Frisbee Count (expected 4; distance: %s)" % self.frisbee_sensor.distance)
            
        
    def test_feed(self):
        from components import feeder
        if not getattr(self.tested_feeder, "FEEDER_READY_DISTANCE") :
            raise Exception("Need to set a distance at which the feeder will be ready")
        
        self.frisbee_sensor.distance = FEEDER_READY_DISTANCE
        if not getattr(self.tested_feeder, "feed"):
            raise Exception("Need to set a distance at which the feeder will be ready")
            
        self.tested_feeder.feed()
        
        if self.feeder_motor.speed != 0:
            raise Exception("Update must be called to start the motor")
        self.tested_feeder.update()
        
        if self.feeder_motor.speed != 1:
            raise Exception("Feeder should start")
                    
        self.frisbee_sensor.distance = FEEDER_READY_DISTANCE + 5
        
        self.tested_feeder.feed()
        if self.feeder_motor.speed != 0:
            raise Exception("Update must be called to start the motor")
        self.tested_feeder.update()
        if self.feeder_motor.speed != 1:
            raise Exception("Feeder is ready, should go at full speed")
        self.tested_feeder.update()
        if self.feeder_motor.speed != 0:
            raise Exception("Feeder made full circle should stop")
            
        
   
        
class Test_Sensor(wpilib.AnalogChannel):

    
    def __init__(self,channel):
        super().__init__(channel)
        self.distance = 0
    def GetDistance(self):
        return self.distance
   
   
def run_test():
    test = Test()
    test.test_get_frisbee_count()
    test.test_feed()