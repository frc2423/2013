print( "Loading: Kwarqs2013 electrical testing program" )

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

#CAN Motoros
shooter_motor = wpilib.CANJaguar(1)
angle_motor = wpilib.CANJaguar(2)
feed_motor = wpilib.CANJaguar(3)

#needs to be connected to jaguar
#chamber_sensor dectets frisbees being held
chamber_sensor = wpilib.AnalogChannel(5)
#Motor Speeds
feed_motor_spd = 1

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
        dog.SetExperation(0.25)
    
        while self.IsOperatorControl() and self.IsEnabled():
            self.drive.ArcadeDrive(stick1)
            #Feed Motor
            if stick2.GetTrigger():
                feed_motor.Set(feed_motor_spd)
                
            feed_motor_postion = feed_motor.GetPosition()
                
            #Shooter Motor
            
            shooter_motor_spd = 1
            shooter_motor.Set(GetZ)
            
            #display on SmartDashboard current spd and set spd
            #Angle Motor
            
            
            angle_motor_position = angle_motor.GetPosition()
            angle_motor.Set(GetY)
                
            frisbee_count = chamber_sensor.Get()
                
            shooter_encoder_position = shooter_motor.GetPosition()
            
            wpilib.SmartDashboard.PutDouble(feedMotor, feed_motor_spd)
            wpilib.SmartDashboard.PutDouble(angleMotor, angle_motor_position)
            wpilib.SmartDashboard.PutDouble(frisbeeCount, frisbee_count)
            wpilib.SmartDashboard.PutDouble(shooterEncoder, shooter_encoder_position)
            
            dog.Feed()
            wpilib.Wait(0.04)
def run():
    robot = MyRobot()
    robot.StartCompetition()
    
    return robot