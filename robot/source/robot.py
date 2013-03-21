
try:
    import wpilib 
except ImportError:
    import fake_wpilib as wpilib
    

from autonomous import AutonomousModeManager
from operator_control import OperatorControlManager

from common.auto_jaguar import AnglePositionJaguar, SpeedJaguar
#from common.bang_bang_jaguar import BangBangJaguar
from common.ez_can_jaguar import EzCANJaguar
from common.generic_distance_sensor import GenericDistanceSensor, GP2D120
from common.joystick_util import *

from components.climber import Climber
from components.driving import Driving
from components.feeder_pro import FeederPro
from components.shooter_platform import ShooterPlatform
from components.target_detector import TargetDetector

from systems.shooter import Shooter
from systems.climber import ClimberSystem
from systems.auto_targeting import AutoTargeting
from systems.robot_turner import RobotTurner



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
valve1_channel = 2
valve2_channel = 1


#
#    Create robot motors/sensors here
#

#PWM Motors
l_motor = wpilib.Jaguar(l_motor_pwm)
r_motor = wpilib.Jaguar(r_motor_pwm)

#CAN Motors

# tuned using information from http://www.chiefdelphi.com/forums/showpost.php?p=1112886&postcount=37
SHOOTER_P = -0.05
SHOOTER_I = -0.0028
SHOOTER_D = 0

shooter_motor = EzCANJaguar(shooter_motor_can)
shooter_motor.SetSpeedReference(wpilib.CANJaguar.kSpeedRef_QuadEncoder)
shooter_motor.ConfigEncoderCodesPerRev(1000)
shooter_motor.SetPID(SHOOTER_P, SHOOTER_I, SHOOTER_D)


# these parameters are necessary for bang-bang mode
shooter_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Coast)
shooter_motor.SetVoltageRampRate(0.0)
shooter_motor_threshold = 100

ANGLE_P = -3000.0 
ANGLE_I = -0.1 
ANGLE_D = -14.0

ANGLE_MIN_POSITION = 0.594
ANGLE_MAX_POSITION = 0.498
ANGLE_MIN_ANGLE    = 25.6
ANGLE_MAX_ANGLE    = -0.2 # TODO

angle_motor = EzCANJaguar(angle_motor_can)
angle_motor.SetPositionReference(wpilib.CANJaguar.kPosRef_Potentiometer)
angle_motor.ConfigPotentiometerTurns(1)
angle_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Coast)
angle_motor.SetPID(ANGLE_P, ANGLE_I, ANGLE_D)
angle_motor_threshold = 0.1

feeder_motor = EzCANJaguar(feeder_motor_can)
feeder_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)

# compressor for pneumatics 
compressor = wpilib.Compressor(compressor_switch, compressor_relay)


# solenoids for climber
# -> TODO: should we use the DoubleSolenoid class instead?
valve1 = wpilib.Solenoid(valve1_channel)
valve2 = wpilib.Solenoid(valve2_channel)

# drive object
drive = wpilib.RobotDrive(l_motor, r_motor)

# TODO: Fix this. 
drive.SetSafetyEnabled(False)


# sensors connected to jags: frisbee_sensor detects frisbees being held
frisbee_sensor = GenericDistanceSensor(frisbee_sensor_channel, GP2D120)
feeder_sensor = GenericDistanceSensor(feeder_sensor_channel, GP2D120)
shooter_sensor = GenericDistanceSensor(shooter_sensor_channel, GP2D120)

# relay
camera_led = wpilib.Relay(camera_led_relay)
camera_led.Set(wpilib.Relay.kForward)

# thresholds

speed_threshold = 100

# control loop time
control_loop_wait_time = 0.025



                                                            
class MyRobot(wpilib.SimpleRobot):
    
    # import into this namespace
    ANGLE_MIN_ANGLE = ANGLE_MIN_ANGLE
    ANGLE_MAX_ANGLE = ANGLE_MAX_ANGLE
    
    # keep in sync with driver station
    MODE_DISABLED       = 1
    MODE_AUTONOMOUS     = 2
    MODE_TELEOPERATED   = 3
    
    def __init__(self):
        wpilib.SimpleRobot.__init__(self)
        
        self.ds = wpilib.DriverStation.GetInstance()
        self.sd = wpilib.SmartDashboard
             
        # create the component instances
        climber = Climber(valve1, valve2)
        
        self.my_drive = Driving(drive)
        
        self.my_feeder = FeederPro(feeder_motor, 
                                   frisbee_sensor, 
                                   feeder_sensor)
        
        auto_angle = AnglePositionJaguar(angle_motor, angle_motor_threshold,
                                         ANGLE_MIN_POSITION, ANGLE_MAX_POSITION,
                                         ANGLE_MIN_ANGLE, ANGLE_MAX_ANGLE)
        auto_shooter = SpeedJaguar(shooter_motor, shooter_motor_threshold)
        
        # Bang-bang doesn't work on a Jaguar.. 
        #auto_shooter = BangBangJaguar(shooter_motor, shooter_motor_threshold)
        
        self.my_shooter_platform = ShooterPlatform(auto_angle,
                                                   auto_shooter,
                                                   climber)
        
        self.my_target_detector = TargetDetector()
        
        # create the system instances
        self.my_robot_turner = RobotTurner(self.my_drive)
        self.my_auto_targeting = AutoTargeting(self.my_robot_turner, self.my_shooter_platform, self.my_target_detector)
        self.my_climber = ClimberSystem(climber, self.my_shooter_platform)
        
        self.my_shooter = None # TODO
        
        # autonomous mode needs a dict of components
        components = {
            # components 
            'drive': self.my_drive,
            'feeder': self.my_feeder,
            'shooter_platform': self.my_shooter_platform,
            'target_detector': self.my_target_detector, 
            
            # systems
            'auto_targeting': self.my_auto_targeting,
            'climber': self.my_climber,
            'robot_turner': self.my_robot_turner,
            #'shooter': self.my_shooter,
        }

        self.components = []
        self.components = [v for v in components.values() if hasattr(v, 'update')]
        self.components.append(climber)
        self.autonomous_mode = AutonomousModeManager(components)
        self.operator_control_mode = OperatorControlManager(components, self.ds)
        
        # initialize other needed SmartDashboard inputs
        self.sd.PutBoolean("Wheel On", False)
        self.sd.PutBoolean("Auto Feeder", True)
        self.sd.PutBoolean("Fire", False)
    
        
    def RobotInit(self):
        pass

    def Disabled(self):
        print("MyRobot::Disabled()")
        
        self.sd.PutNumber("Robot Mode", self.MODE_DISABLED)
    
        while self.IsDisabled():
            wpilib.Wait(control_loop_wait_time)
            
    def Autonomous(self):        
        print("MyRobot::Autonomous()")
        
        self.sd.PutNumber("Robot Mode", self.MODE_AUTONOMOUS)
        
        # put this in a consistent state when starting the robot
        self.my_climber.lower()
        
        # this does all the autonomous mode work for us
        self.autonomous_mode.run(self, control_loop_wait_time)
        
    def OperatorControl(self):
        
        print("MyRobot::OperatorControl()")
        
        self.sd.PutNumber("Robot Mode", self.MODE_TELEOPERATED)
        
        # set the watch dog
        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExpiration(0.25)
        
        compressor.Start()   
        
        # All operator control functions are now in OperatorControlManager   
        self.operator_control_mode.run(self, control_loop_wait_time)

        #
        # Done with operator mode, finish up
        #
        compressor.Stop()     
    
    #
    #    Other
    #
                
    def update(self):
        '''Runs update on all components'''
        for component in self.components:
            component.update()
        

def run():
    
    # this is initialized in StartCompetition, but one of our
    # constructors might use it, and crash
    wpilib.SmartDashboard.init()
    
    robot = MyRobot()
    robot.StartCompetition()
    
    return robot


