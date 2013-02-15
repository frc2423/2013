
from autonomous import AutonomousModeManager
from components import generic_distance_sensor

try:
    import wpilib 
except ImportError:
    import fake_wpilib as wpilib 
    
    #Variables as strings
switch_1 = "Switch 1"
switch_2 = "Switch 2"
angleMotor = "Angle Motor"
feedMotor = "Feed Motor"
shooterEncoder = "Shooter Encoder"
frisbeeCount = "Frisbee Count"

#Joysticks
stick1 = wpilib.Joystick(1)
stick2 = wpilib.Joystick(2)

#PWM Motors
l_motor = wpilib.Jaguar(2)
r_motor = wpilib.Jaguar(1)

#CAN Motors
shooter_motor = wpilib.CANJaguar(7)
angle_motor = wpilib.CANJaguar(4)
feed_motor = wpilib.CANJaguar(5)

#sensors connected to jags: chamber_sensor detects frisbees being held
chamber_sensor = generic_distance_sensor.GenericDistanceSensor(3, generic_distance_sensor.E4P_250_250)
feed_sensor = generic_distance_sensor.GenericDistanceSensor(4, generic_distance_sensor.E4P_250_250)
shooter_sensor = generic_distance_sensor.GenericDistanceSensor(5, generic_distance_sensor.E4P_250_250)

#motor positions
feed_motor_postion = feed_motor.GetPosition()
angle_motor_position = angle_motor.GetPosition()
shooter_encoder_position = shooter_motor.GetPosition()

# counting frisbees
frisbee_count = chamber_sensor.Get()

#Motor Speeds
feed_motor_spd = 1
shooter_motor_spd = 1

#Loop time
control_loop_wait_time = 0.02

# TODO
components = {}
autonomous_mode = AutonomousModeManager(components)

class MyRobot(wpilib.SimpleRobot):

    def __init__(self):
        wpilib.SimpleRobot.__init__(self)

    def RobotInit(self):
        pass

    def Disabled(self):
        print("MyRobot::Disabled()")
    
        while self.IsDisabled():
            wpilib.Wait(control_loop_wait_time)
            
    def Autonomous(self):        
        print("MyRobot::Autonomous()")
        
        # this does all the autonomous mode work for us
        autonomous_mode.run(self, control_loop_wait_time)
        
    def OperatorControl(self):
        print("MyRobot::OperatorControl()")
        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExperation(0.25)
        while self.IsOperatorControl():
            pass
    
        self.wpilib.SmartDashboard.PutNumber('feed_motor', feed_motor_spd)
        self.wpilib.SmartDashboard.PutNumber('angle_motor', angle_motor_position)
        self.wpilib.SmartDashboard.PutNumber('frisbee_count', frisbee_count)
        self.wpilib.SmartDashboard.PutNumber('shooter_encoder', shooter_encoder_position)
        
        dog.Feed()
        wpilib.Wait(control_loop_wait_time)
            

        

def run():
    robot = MyRobot()
    robot.StartCompetition()
    
    return robot



