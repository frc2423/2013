print( "Loading: Kwarqs2013 electrical testing program" )

#from components import generic_distance_sensor
try:    
    import wpilib
except ImportError:
    import fake_wpilib as wpilib
    
    
#Variables
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
feed_motor = wpilib.CANJaguar(6)

drive = wpilib.RobotDrive(l_motor, r_motor)
drive.SetSafetyEnabled(False)

#needs to be connected to jaguar
#chamber_sensor detects frisbees being held
#chamber_sensor = generic_distance_sensor.GenericDistanceSensor(3, generic_distance_sensor.E4P_250_250)
#feed_sensor = generic_distance_sensor.GenericDistanceSensor(4, generic_distance_sensor.E4P_250_250)
#shooter_sensor = generic_distance_sensor.GenericDistanceSensor(5, generic_distance_sensor.E4P_250_250)

#Motor Speeds
feed_motor_spd = 1

feed_motor_postion = feed_motor.GetPosition()

class MyRobot(wpilib.SimpleRobot):

    def __init__(self):
        '''Constructor'''
        
        wpilib.SimpleRobot.__init__(self)

    def RobotInit(self):
        pass

    def Disabled(self):

        print("MyRobot::Disabled()")
    
        while self.IsDisabled():
            wpilib.Wait(0.01)
            
    def Autonomous(self):
    
        '''Called during autonomous mode'''
        
        print("MyRobot::Autonomous()")
    
        self.GetWatchdog().SetEnabled(False)
        while self.IsAutonomous() and self.IsEnabled():
            wpilib.Wait(0.01)
        
    def OperatorControl(self):
    
        print("MyRobot::OperatorControl()")
        
        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExpiration(0.25)
    
        while self.IsOperatorControl() and self.IsEnabled():
            drive.ArcadeDrive(stick1)
            
            #Feed Motor
            if stick1.GetTrigger():
                feed_motor.Set(stick1.GetZ())
                
            #Shooter Motor
            if stick2.GetTrigger():
                shooter_motor.Set(stick2.GetZ())
            
            #display on SmartDashboard current spd and set spd
            #Angle Motor
            
            
            angle_motor_position = angle_motor.GetPosition()
            angle_motor.Set(stick2.GetY())
                
            #frisbee_count = chamber_sensor.Get()
                
            shooter_encoder_position = shooter_motor.GetPosition()
            
            #self.wpilib.SmartDashboard.PutNumber(feedMotor, feed_motor_spd)
            wpilib.SmartDashboard.PutNumber(angleMotor, angle_motor_position)
            #self.wpilib.SmartDashboard.PutNumber(frisbeeCount, frisbee_count)
            wpilib.SmartDashboard.PutNumber(shooterEncoder, shooter_encoder_position)
            
            dog.Feed()
            wpilib.Wait(0.04)
            
            
def run():
    robot = MyRobot()
    robot.StartCompetition()
    
    return robot
