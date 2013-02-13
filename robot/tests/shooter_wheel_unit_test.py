'''
    This is a unit test of shooter_wheel.py. It is designed to test both expected 
    functionality as well as if code is written correctly. If naming
    conventions are not followed this will break the test. If functionality
    is incorrect this test will print out failure
'''

# directory of component to test
robot_path = '../../robot/source/components'
import_robot = False

import inspect
import fake_wpilib as wpilib

def lineno():
    #returns current line
    return inspect.currentframe().f_back.f_lineno

class Test(object):
    
    def __init__(self, angle_threshold, speed_threshold):
        import shooter_wheel
        self.angleMotor = wpilib.CANJaguar(1,wpilib.CANJaguar.kPosition)
        self.angleMotor.SetPositionReference(wpilib.CANJaguar.kPosRef_Potentiometer)
                
        self.shooterMotor = wpilib.CANJaguar(2)
        self.shooterMotor.SetSpeedReference(wpilib.CANJaguar.kSpeedRef_Encoder)
        
        try:
            self.tested_shooter_wheel = shooter_wheel.ShooterWheel(self.angleMotor, self.shooterMotor,\
                                                                   angle_threshold, speed_threshold)
        except TypeError:
            print("ERROR: ShooterWheel is taking the wrong number of parameters")
    def test_set_speed(self, speed):
        self.speed = speed
        if getattr(self.tested_shooter_wheel, "set_speed"):
            self.tested_shooter_wheel.set_speed(self.speed)
            if self.shooterMotor.GetSpeed() != 0:
                print("Error: Shooter speed set before update function called! ",\
                      " line: ", lineno())
        else:
            print("Error: no set_speed function available line: ", lineno())
    
    def test_set_angle(self, angle):
        self.angle = angle
        if getattr(self.tested_shooter_wheel, "set_angle"):
            self.tested_shooter_wheel.set_angle(self.angle)
            if self.angleMotor.GetPosition() != 0:
                print("Error: Shooter angle set before update function called!",\
                      " line: ", lineno())
        else:
            print("Error: no set_speed function available line: ", lineno())
    
    def test_is_ready(self, angle, speed):
        self.shooterMotor.speed = 0
        self.angleMotor.position = 0
        self.test_set_speed(speed)
        self.test_set_angle(angle)
        if getattr(self.tested_shooter_wheel, "is_ready"):
        
            #shouldn't be ready yet
            if self.tested_shooter_wheel.is_ready() == True:
                print("ERROR: Shooter should not be ready yet line: ", lineno())
            #now the shooter should be ready
            self.shooterMotor.speed = speed
            self.angleMotor.position = angle
            
            print ('test angle =' , angle)
            print ('angleMotor.position() =', self.angleMotor.GetPosition())
            if self.tested_shooter_wheel.is_ready() == False:
                print("ERROR: Shooter should be ready now line: ", lineno())
        
        else:
            
            print("ERROR: No is_ready function available line: ", lineno())

    
    def test_update(self,angle, speed):
        if getattr(self.tested_shooter_wheel, "update"):
            #clear speed out
            self.shooterMotor.speed = 0
            self.shooterMotor.value = 0
            self.angleMotor.position = 0
            self.angleMotor.value = 0
            #set our goals
            self.test_set_speed(speed)
            self.test_set_angle(angle)
            #update our shooter
            self.tested_shooter_wheel.update()
            
            if self.shooterMotor.value != 1: 
                print("Error: Shooter Motor set incorrectly, should be set to 1")
                
            if self.angleMotor.value != angle:
                print("Error: Angle Motor set incorrectly, should be set to" , \
                        angle, " line: ", lineno())
            #our speed has over shot    
            self.shooterMotter.speed = speed + 1
            
            self.tested_shooter_wheel.update()
            
            if self.shooterMotor.value != 0:
                print("Error: Shooter Motor set incorrectly, should be set to 0")
            
def run_test():
    test = Test(1,1)
    test.test_is_ready(40,40)
    test.test_update