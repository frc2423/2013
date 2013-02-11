'''
    This is a unit test of driving.py. It is designed to test both expected 
    functionality as well as if code is written correctly. If naming
    conventions are not followed this will break the test. If functionality
    is incorrect this test will print out failure
'''

# directory of component to test
robot_path = '../../robot/source/'
import_robot = False

import inspect
import fake_wpilib as wpilib

def lineno():
    #returns current line
    return inspect.currentframe().f_back.f_lineno

class Test(object):
    
    def __init__(self):
        from components import feeder
        
        self.feeder_motor = wpilib.CANJaguar(1)
        self.frisbee_sensor = wpilib.AnalogChannel(1)
        self.feed_sensor = wpilib.AnalogChannel(2)
        self.tested_feeder = feeder.Feeder(self.feeder_motor,self.frisbee_sensor, self.feed_sensor)
        
    def test_get_frisbee_count(self):
        from components import feeder
        self.frisbee_sensor.voltage = 0
        if hasattr(self.tested_feeder, "get_frisbee_count"):
            if self.tested_feeder.get_frisbee_count() != 0:
                raise Exception("Wrong Frisbee Count")
            
            self.frisbee_sensor.voltage = feeder.ZERO_FRISBEE
            
            if self.tested_feeder.get_frisbee_count() != 0:
                raise Exception("Wrong Frisbee Count")
            
            self.frisbee_sensor.voltage = feeder.ONE_FRISBEE
            
            if self.tested_feeder.get_frisbee_count() != 1:
                raise Exception("Wrong Frisbee Count")
            
            self.frisbee_sensor.voltage = feeder.TWO_FRISBEE
            
            if self.tested_feeder.get_frisbee_count() != 2:
                raise Exception("Wrong Frisbee Count")
            
            self.frisbee_sensor.voltage = feeder.THREE_FRISBEE
            
            if self.tested_feeder.get_frisbee_count() != 3:
                raise Exception("Wrong Frisbee Count")
            
            self.frisbee_sensor.voltage = feeder.FOUR_FRISBEE
            
            if self.tested_feeder.get_frisbee_count() != 4:
                raise Exception("Wrong Frisbee Count")
        else:
            raise Exception("Please use proper naming conventions")
        
    def test_feed(self):
        from components import feeder
        if getattr(self.tested_feeder, "FEEDER_READY_DISTANCE") :
            self.frisbee_sensor.distance = 1000
            self.frisbee_sensor.voltage = 3
            if getattr(self.tested_feeder, "feed"):
                self.feed()
                
                if self.feeder_motor.speed != 0:
                    raise Exception("Update must be called to start the motor")
                self.update()
                
                if self.feeder_motor.speed != 0:
                    raise Exception("Feeder is not ready, should not start")
                            
                self.frisbee_sensor.distance = 10
                self.frisbee_sensor.voltage = 1
                self.feed()
                if self.feeder_motor.speed != 0:
                    raise Exception("Update must be called to start the motor")
                self.update()
                if self.feeder_motor.speed != 1:
                    raise Exception("Feeder is ready, should go at full speed")
                self.update()
                if self.feeder_motor.speed != 0:
                    raise Exception("Feeder made full circle should stop")
                
            else:
                raise Exception("Need to set a distance at which the feeder will be ready")
        else:
            raise Exception("Need to set a distance at which the feeder will be ready")
   
        
class Test_Sensor(wpilib.AnalogChannel):

    
    def __init__(self,channel):
        wpilib.AnalogChannel.__init__()
        self.distance = 0
    def get_distance(self):
        return self.distance
   
   
def run_test():
    test = Test()
    '''test.test_get_frisbee_count()'''
    test.test_feed()