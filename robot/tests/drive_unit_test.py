'''
    This is a unit test of driving.py. It is designed to test both expected 
    functionality as well as if code is written correctly. If naming
    conventions are not followed this will break the test. If functionality
    is incorrect this test will print out failure
'''

# directory of component to test
robot_path = '../../robot/source/components'
import_robot = False

import fake_wpilib as wpilib

# make importing _unittest_util possible
sys.path.append(os.path.dirname(__file__))
import _unittest_util


class Test(object):
    
    def __init__(self):
        import driving
        self.l_motor = wpilib.Jaguar(1)
        self.r_motor = wpilib.Jaguar(2)
        self.drive = wpilib.RobotDrive(self.l_motor, self.r_motor)
        self.tested_driver = driving.Driving(self.drive)
        
        _unittest_util.validate_docstrings(self.tested_driver)
    
    def _get_motor_values(self,speed, rotation):
        '''
            gets values of individual motor speeds
        '''
        if speed > 0.0:
            if rotation > 0.0:
                leftMotorOutput = speed - rotation
                rightMotorOutput = max(speed, rotation)
            else:
                leftMotorOutput = max(speed, -rotation)
                rightMotorOutput = speed + rotation
        else:
            if rotation > 0.0:
                leftMotorOutput = -max(-speed, rotation)
                rightMotorOutput = speed + rotation
            else:
                leftMotorOutput = speed - rotation
                rightMotorOutput = -max(-speed, -rotation)
                
        return leftMotorOutput, rightMotorOutput
    
    def test_drive(self,speed, rotation):
        #test 1, check if speed and rotation set correctly
        leftMotorOutput, rightMotorOutput = self._get_motor_values(speed,rotation)
        
        if getattr(self.tested_driver, "drive"):
            self.tested_driver.drive(rotation, speed)
            
            if self.l_motor.Get() != 0 and \
            self.r_motor.Get != 0:
                
                print("Motor speeds set before update called")
                    
            if getattr(self.tested_driver, "drive"):
                self.tested_driver.update()
                
                if self.l_motor.Get() != leftMotorOutput and \
                self.r_motor.Get != rightMotorOutput:
                    
                    print("Motor speeds not set correctly in Test")
            else:
                print("ERROR: no update function available")
        
        else:
            print("ERROR: No drive function available")
    
def run_test():
    test = Test()
    test.test_drive(1,.5)
    