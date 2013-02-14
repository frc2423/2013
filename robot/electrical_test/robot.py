
print( "Loading: Kwarqs2013 electrical testing program" )

try:    
    import wpilib
except ImportError:
    import fake_wpilib as wpilib

#Joysticks
stick1 = wpilib.Joystick(1)
stick2 = wpilib.Joystick(2)

#PWM Motors
l_motor = wpilib.Jaguar(2)
r_motor = wpilib.Jaguar(1)

#CAN Motors
shooter_motor = wpilib.CANJaguar(7)
shooter_motor.SetSpeedReference(wpilib.CANJaguar.kSpeedRef_QuadEncoder)
shooter_motor.ConfigEncoderCodesPerRev(360)
shooter_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)

angle_motor = wpilib.CANJaguar(4)
angle_motor.SetPositionReference(wpilib.CANJaguar.kPosRef_Potentiometer)
angle_motor.ConfigPotentiometerTurns(1)
angle_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)

loader_cam_motor = wpilib.CANJaguar(6)


# optical sensors
loader_sensor = wpilib.AnalogChannel(3)
loader_cam_sensor = wpilib.AnalogChannel(4)
shooter_detect_sensor = wpilib.AnalogChannel(5)


# drive object
drive = wpilib.RobotDrive(l_motor, r_motor)

# TODO: Fix this. 
drive.SetSafetyEnabled(False)

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
            
            # measure loop time
            start = wpilib.Timer.GetPPCTimestamp()
            
            drive.ArcadeDrive(stick1)
            
            # loader cam motor
            if stick1.GetTrigger():
                loader_cam_motor.Set(stick1.GetZ())
                
            # shooter wheel motor
            if stick2.GetTrigger():
                shooter_motor.Set(stick2.GetZ())
            
            # Angle motor
            angle_motor.Set(stick2.GetY())
                
            # sensor status
            wpilib.SmartDashboard.PutNumber('Loader', loader_sensor.GetVoltage())
            wpilib.SmartDashboard.PutNumber('Loader cam', loader_cam_sensor.GetVoltage())
            wpilib.SmartDashboard.PutNumber('Shooter detect', shooter_detect_sensor.GetVoltage())
            
            # motor status
            wpilib.SmartDashboard.PutNumber('Angle', angle_motor.GetPosition())
            wpilib.SmartDashboard.PutBoolean('Angle Limit Forward', angle_motor.GetForwardLimitOK())
            wpilib.SmartDashboard.PutBoolean('Angle Limit Reverse', angle_motor.GetReverseLimitOK())
            wpilib.SmartDashboard.PutNumber('Shooter wheel speed', shooter_motor.GetSpeed())
            
            dog.Feed()
            
            # how long does it take us to run the loop?
            wpilib.SmartDashboard.PutNumber('Loop time', wpilib.Timer.GetPPCTimestamp() - start)
            
            wpilib.Wait(0.04)
            
        dog.SetEnabled(False)
            
            
def run():
    robot = MyRobot()
    robot.StartCompetition()
    
    return robot
