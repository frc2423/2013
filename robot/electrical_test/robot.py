print( "Loading: Kwarqs2013 electrical testing program" )

try:    
    import wpilib
except ImportError:
    import fake_wpilib as wpilib

#Joysticks
stick1 = wpilib.Joystick(1)
stick2 = wpilib.Joystick2(2)    

#PWM Motors
l_motor = wpilib.Jaguar(2)
r_motor = wpilib.Jaguar(1)
feed_motor = wpilib.Jaguar(3)


#CAN Motoros
shooter_motor = wpilib.CANJaguar
angle_motor = wpilib.CANJaguar

shooter_encoder = wpilib.Encoder(10,11)

chamber_sensor = wpilib.AnalogChannel(5)

switch1 = wpilib.DigitalInput(1)
switch2 = wpilib.DigitalInput(2)

potentiometer = wpilib.DigitalInput(3)

set_wheel_spd = 28

ANGLE_MOTOR_MIN_POSITION = 0.0
ANGLE_MOTOR_MAX_POSITION = 1.0
ANGLE_MOTOR_P = 250.0
ANGLE_MOTOR_I = 0.0
ANGLE_MOTOR_D = 0.0

# shooter wheel stuff
ENCODER_TURNS_PER_REVOLUTION = 360
        
SHOOTER_MOTOR_P = 100.0
SHOOTER_MOTOR_I = 0.0
SHOOTER_MOTOR_D = 0.0

#Motor Speeds
feed_motor_spd = 1

class MyRobot(wpilib.SimpleRobot):

    def __init__(self):
        '''Constructor'''
        
        wpilib.SimpleRobot.__init__(self)
        self.drive = wpilib.RobotDrive( l_motor, r_motor )
        angle_motor.SetPositionReference( wpilib.CANJaguar.kPosRef_Potentiometer )
        angle_motor.ConfigPotentiometerTurns( 1 )
        shooter_encoder.SetDistancePerPulse( 1.0 / 16.0 )
        shooter_encoder.Start()

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
        
        dog =self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExperation(0.25)
        
        timer = wpilib.Timer()
        timer.Start()

        self.drive.ArcadeDrive(stick1)
        
        #Feed Motor
        if stick2.GetTrigger():
            feed_motor.Set(feed_motor_spd)
           

        
        #Shooter Motor
        if stick2.GetRawButton(2):
            shooter_motor_spd = 1
            shooter_motor.Set(shooter_motor_spd)
            #display on SmartDashboard current spd and set spd
        
        if stick1.GetRawButton(3):
            #make angle move up by certain amount. Confused by P I D variables.
            
        
        while self.IsOperatorControl() and self.IsEnabled():
            dog.Feed()
            wpilib.Wait(0.04)

def run():
    robot = MyRobot()
    robot.StartCompetition()
    
    return robot