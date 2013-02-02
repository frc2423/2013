print( "Loading: Kwarqs2013 electrical testing program" )

try:    
    import wpilib
    import wpilib.SmartDashboard
except ImportError:
    import fake_wpilib as wpilib
    import fake_wpilib.SmartDashboard

#Joysticks
stick1 = wpilib.Joystick(1)
stick2 = wpilib.Joystick(2)

#PWM Motors
l_motor = wpilib.Jaguar(2)
r_motor = wpilib.Jaguar(1)


#Variables
switch_1 = "Switch 1"
switch_2 = "Switch 2"
AngleMotor = "Angle Motor"
FeedMotor = "Feed Motor"
ShooterEncoder = "Shooter Encoder"
FrisbeeCount = "Frisbee Count"
#CAN Motoros
shooter_motor = wpilib.CANJaguar(1)
angle_motor = wpilib.CANJaguar(2)
feed_motor = wpilib.CANJaguar(3)
#needs to be connected Jaguar
shooter_encoder = wpilib.AnalogChannel(1)
#needs to be connected to jaguar
#chamber_sensor dectets frisbees being held
chamber_sensor = wpilib.AnalogChannel(5)
#switches limit angle motor movement
switch1 = wpilib.DigitalInput(1)
switch2 = wpilib.DigitalInput(2)

potentiometer = wpilib.DigitalInput(3)

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
        
        timer = wpilib.Timer()
        timer.Start()

        
        
        while self.IsOperatorControl() and self.IsEnabled():
            self.drive.ArcadeDrive(stick1)
            #Feed Motor
            if stick2.GetTrigger():
                feed_motor.Set(feed_motor_spd)
            if stick2.GetRawButton(1):
                feed_motor_postion = feed_motor.GetPosition()
            #Shooter Motor
            if stick2.GetRawButton(2):
                shooter_motor_spd = 1
                shooter_motor.Set(shooter_motor_spd)
            #display on SmartDashboard current spd and set spd
            #Angle Motor
            if stick2.GetRawButton(3):
                angle_motor_position = angle_motor.GetPosition()
            if stick2.GetRawButton(4):
                frisbee_count = chamber_sensor.Get()
            if stick2.GetRawButton(5):
                shooter_encoder_position = shooter_encoder.Get()
            dog.Feed()
            wpilib.Wait(0.04)
            SmartDashboard.PutDouble(FeedMotor, feed_motor_spd)
            SmartDashboard.PutDouble(AngleMotor, angle_motor_position)
            SmartDashboard.PutDouble(FrisbeeCount, frisbee_count)
            SmartDashboard.PutDouble(ShooterEncoder, shooter_encoder_position)
def run():
    robot = MyRobot()
    robot.StartCompetition()
    
    return robot