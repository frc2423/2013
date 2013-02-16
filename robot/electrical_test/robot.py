
print( "Loading: Kwarqs2013 electrical testing program" )

try:    
    import wpilib
except ImportError:
    import fake_wpilib as wpilib

#
#    Declare all the ports and channels here
#    Note: these are shared between the electrical test and main code!
#

# PWM channels
l_motor_pwm = 1
r_motor_pwm = 2

# CAN channels
loader_cam_can = 3
angle_motor_can = 4
shooter_wheel_can = 7

# Relay channels
camera_led_relay = 1
compressor_relay = 2

# Analog channels
loader_sensor_analog = 3
loader_cam_sensor_analog = 4
shooter_detect_sensor = 5

# Digital channels
compressor_switch = 1

# Solenoids
valve1_channel = 1
valve2_channel = 2


#
#    Create robot motors/sensors here
#


#Joysticks
stick1 = wpilib.Joystick(1)
stick2 = wpilib.Joystick(2)

#PWM Motors
l_motor = wpilib.Jaguar(l_motor_pwm)
r_motor = wpilib.Jaguar(r_motor_pwm)

#CAN Motors

# shooter: -1 is full on
shooter_motor = wpilib.CANJaguar(shooter_wheel_can)
shooter_motor.SetSpeedReference(wpilib.CANJaguar.kSpeedRef_QuadEncoder)
shooter_motor.ConfigEncoderCodesPerRev(360)
shooter_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)

angle_motor = wpilib.CANJaguar(angle_motor_can)
angle_motor.SetPositionReference(wpilib.CANJaguar.kPosRef_Potentiometer)
angle_motor.ConfigPotentiometerTurns(1)
angle_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)

loader_cam_motor = wpilib.CANJaguar(loader_cam_can)


# optical sensors
loader_sensor = wpilib.AnalogChannel(loader_sensor_analog)
loader_cam_sensor = wpilib.AnalogChannel(loader_cam_sensor_analog)
shooter_detect_sensor = wpilib.AnalogChannel(shooter_detect_sensor)

# compressor
compressor = wpilib.Compressor(compressor_switch, compressor_relay)
compressor.Start()

# solenoids
valve1 = wpilib.Solenoid(valve1_channel)
valve2 = wpilib.Solenoid(valve2_channel)


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
            else:
                loader_cam_motor.Set(0)
                
            # shooter wheel motor
            if stick2.GetTrigger():
                shooter_motor.Set(stick2.GetZ())
            else:
                shooter_motor.Set(0)
            
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
