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
feeder_motor_can = 3
angle_motor_can = 4
shooter_motor_can = 7

# Relay channels
camera_led_relay = 2
compressor_relay = 1

# Analog channels
frisbee_sensor_channel = 5
feeder_sensor_channel = 4
shooter_sensor_channel = 3

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
shooter_motor = wpilib.CANJaguar(shooter_motor_can)
shooter_motor.SetSpeedReference(wpilib.CANJaguar.kSpeedRef_QuadEncoder)
shooter_motor.ConfigEncoderCodesPerRev(1000)
shooter_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)

angle_motor = wpilib.CANJaguar(angle_motor_can)
angle_motor.SetPositionReference(wpilib.CANJaguar.kPosRef_Potentiometer)
angle_motor.ConfigPotentiometerTurns(1)
angle_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)

feeder_motor = wpilib.CANJaguar(feeder_motor_can)
feeder_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)

# shooter wheel stuff
        
SHOOTER_MOTOR_P = 100.0
SHOOTER_MOTOR_I = 0.0
SHOOTER_MOTOR_D = 0.0

ANGLE_MOTOR_P = 1500.0
ANGLE_MOTOR_I = 0.0
ANGLE_MOTOR_D = 0.0


# enable PID based speed control of the motor.. 
#shooter_motor.ChangeControlMode( wpilib.CANJaguar.kSpeed )
#shooter_motor.SetPID( SHOOTER_MOTOR_P, SHOOTER_MOTOR_I, SHOOTER_MOTOR_D )
#shooter_motor.EnableControl()

#angle_motor.ChangeControlMode( wpilib.CANJaguar.kPosition )
#angle_motor.SetPID( ANGLE_MOTOR_P, ANGLE_MOTOR_I, ANGLE_MOTOR_D )
#angle_motor.EnableControl()


# compressor for pneumatics 
#compressor = wpilib.Compressor(compressor_switch, compressor_relay)
#compressor.Start()

# solenoids for climber
# -> TODO: should we use the DoubleSolenoid class instead?
valve1 = wpilib.Solenoid(valve1_channel)
valve2 = wpilib.Solenoid(valve2_channel)

# optical sensors
frisbee_sensor = wpilib.AnalogChannel(frisbee_sensor_channel)
feeder_sensor = wpilib.AnalogChannel(feeder_sensor_channel)
shooter_sensor = wpilib.AnalogChannel(shooter_sensor_channel)


# relay
camera_led = wpilib.Relay(camera_led_relay)
camera_led.Set(wpilib.Relay.kForward)

# drive object
drive = wpilib.RobotDrive(l_motor, r_motor)

# TODO: Fix this. 
drive.SetSafetyEnabled(False)

wpilib.SmartDashboard.init()



class MyRobot(wpilib.SimpleRobot):

    def __init__(self):
        '''Constructor'''
        
        wpilib.SimpleRobot.__init__(self)
        
        #wpilib.SmartDashboard.PutNumber('A_P', ANGLE_MOTOR_P )
        #wpilib.SmartDashboard.PutNumber('A_I', ANGLE_MOTOR_I )
        #wpilib.SmartDashboard.PutNumber('A_D', ANGLE_MOTOR_D )
        
    def _translate_z(self, z, zmin, zmax):
    
        # Xmax - (Ymax - Y)( (Xmax - Xmin) / (Ymax - Ymin) )
        return zmax - ((1 - z)*( (zmax - zmin) / 2 ) )
    
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
        
        #p = wpilib.SmartDashboard.GetNumber('A_P')
        #i = wpilib.SmartDashboard.GetNumber('A_I')
        #d = wpilib.SmartDashboard.GetNumber('A_D')
    
        while self.IsOperatorControl() and self.IsEnabled():
            
            # measure loop time
            start = wpilib.Timer.GetPPCTimestamp()
            
            drive.ArcadeDrive(stick1, not stick1.GetTop())
            
            # loader cam motor
            if stick1.GetTrigger():
                feeder_motor.Set(.7)
            else:
                feeder_motor.Set(0)
                
            # shooter wheel motor
            if stick2.GetTrigger():
                shooter_motor.Set(stick2.GetZ())
            else:
                shooter_motor.Set(0)
                
            #lp = wpilib.SmartDashboard.GetNumber('A_P')
            #li = wpilib.SmartDashboard.GetNumber('A_I')
            #ld = wpilib.SmartDashboard.GetNumber('A_D')
            
            #if lp != p or li != i or ld != d:
            #    angle_motor.DisableControl()
            #    angle_motor.SetPID(p, i, d)
            #    angle_motor.EnableControl()
            
            # Angle motor
            #z = self._translate_z(stick1.GetZ(), .505, .59)
            z = stick2.GetZ()
            angle_motor.Set(z)
            
            # Solenoids
            valve1.Set(stick2.GetRawButton(6)) # Makes it go down
            valve2.Set(stick2.GetRawButton(7)) # Makes it go up
                
            # sensor status
            #wpilib.SmartDashboard.PutNumber('Frisbee Sensor', frisbee_sensor.GetVoltage())
            #wpilib.SmartDashboard.PutNumber('Feeder', feeder_sensor.GetVoltage())
            #wpilib.SmartDashboard.PutNumber('Shooter detect', shooter_sensor.GetVoltage())
            
            # motor status
            #wpilib.SmartDashboard.PutNumber('Angle', angle_motor.GetPosition())
            #wpilib.SmartDashboard.PutBoolean('Angle Limit Forward', angle_motor.GetForwardLimitOK())
            #wpilib.SmartDashboard.PutBoolean('Angle Limit Reverse', angle_motor.GetReverseLimitOK())
            #wpilib.SmartDashboard.PutNumber('Shooter wheel speed', shooter_motor.GetSpeed())
            
            dog.Feed()
            
            # how long does it take us to run the loop?
            # -> we're using a lot of globals, what happens when we change it?
            wpilib.SmartDashboard.PutNumber('Loop time', wpilib.Timer.GetPPCTimestamp() - start)
            
            wpilib.Wait(0.04)
            
        dog.SetEnabled(False)
            
            
def run():
    robot = MyRobot()
    robot.StartCompetition()
    
    return robot

