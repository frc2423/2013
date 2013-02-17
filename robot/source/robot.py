
try:
    import wpilib 
except ImportError:
    import fake_wpilib as wpilib
    

from autonomous import AutonomousModeManager

from common.auto_jaguar import PositionJaguar, SpeedJaguar
from common.ez_can_jaguar import EzCANJaguar
from common.generic_distance_sensor import GenericDistanceSensor, GP2D120

from components.climber import Climber
from components.driving import Driving
from components.feeder_pro import FeederPro
from components.shooter_platform import ShooterPlatform
from components.target_detector import TargetDetector

from systems.shooter import Shooter


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
frisbee_sensor_channel = 3
feeder_sensor_channel = 4
shooter_sensor_channel = 5

# Digital channels
compressor_switch = 1

# Solenoids
valve1_channel = 1
valve2_channel = 2


#
#    Create robot motors/sensors here
#

#PWM Motors
l_motor = wpilib.Jaguar(l_motor_pwm)
r_motor = wpilib.Jaguar(r_motor_pwm)

#CAN Motors

# shooter: -1 is full on
shooter_motor = EzCANJaguar(shooter_motor_can)
shooter_motor.SetSpeedReference(wpilib.CANJaguar.kSpeedRef_QuadEncoder)
shooter_motor.ConfigEncoderCodesPerRev(360)
shooter_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)
shooter_motor_threshold = 100

angle_motor = EzCANJaguar(angle_motor_can)
angle_motor.SetPositionReference(wpilib.CANJaguar.kPosRef_Potentiometer)
angle_motor.ConfigPotentiometerTurns(1)
angle_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)
angle_motor_threshold = 0.1

feeder_motor = EzCANJaguar(feeder_motor_can)
feeder_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)

# compressor for pneumatics 
compressor = wpilib.Compressor(compressor_switch, compressor_relay)
compressor.Start()

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

# thresholds

speed_threshold = 100

# control loop time
control_loop_wait_time = 0.02


                                                            
class MyRobot(wpilib.SimpleRobot):
    
    # available toggle switch ports on enhanced EIO
    # -> 2, 4, 8, 12, 16
    
    EIO_CHANNELS = [2,4,8,12,16]
    
    # axis constants
    X = wpilib.Joystick.kDefaultXAxis
    Y = wpilib.Joystick.kDefaultYAxis
    Z = wpilib.Joystick.kDefaultZAxis
    
    # button constants
    TRIGGER = wpilib.Joystick.kDefaultTriggerButton      # 1
    TOP = wpilib.Joystick.kDefaultTopButton              # 2
    
    #
    # Controls configuration
    #
    
    # axis definitions -- a tuple of (stick number, axis)
    # -> call stick_axis() with this value to get the axis
    DRIVE_SPEED_AXIS    = (1, Y)
    DRIVE_ROTATE_AXIS   = (1, X)
    
    SHOOTER_WHEEL_AXIS  = (2, Z)
    PLATFORM_ANGLE_AXIS = (2, Y)
    
    # button definitions -- (stick number, button number)
    # -> call stick_button_on() with this value to get True/False
    
    DRIVE_FASTER_BUTTON     = (1, TOP)
    
    CLIMB_TWIST_L_BUTTON    = (1, 8)
    CLIMB_TWIST_L_BUTTON    = (1, 9)
    
    CLIMB_UP_BUTTON         = (1, 6)
    CLIMB_DOWN_BUTTON       = (1, 7)
    
    FEEDER_FEED_BUTTON      = (2, TRIGGER)
    FEEDER_BACK_BUTTON      = (2, TOP)
    
    # toggle switch definitions
    # -> call is_toggle_on() with this value to get True/False
    
    MANUAL_SHOOTER_ON       = EIO_CHANNELS[0]
    MANUAL_ANGLE_ON         = EIO_CHANNELS[1]
    
    
    def __init__(self):
        wpilib.SimpleRobot.__init__(self)
        
        self.ds = wpilib.DriverStation.GetInstance()
        self.eio = self.ds.GetEnhancedIO()
        
        # initialize the enhanced I/O ports for toggle switches
        
        for channel in self.EIO_CHANNELS:
            self.eio.SetDigitalConfig(channel, wpilib.DriverStationEnhancedIO.kInputFloating)
        
        # create the component instances
        self.my_climber = Climber(valve1, valve2)
        
        self.my_drive = Driving(drive)
        
        self.my_feeder = FeederPro(feeder_motor, 
                                frisbee_sensor, 
                                feeder_sensor)
        
        auto_angle = PositionJaguar(angle_motor, angle_motor_threshold)
        auto_shooter = SpeedJaguar(shooter_motor, shooter_motor_threshold) 
        
        self.my_shooter_platform = ShooterPlatform(auto_angle,
                                                   auto_shooter)
        
        self.my_target_detector = TargetDetector()
        
        # create the system instances
        self.my_shooter = None # TODO
        
        # autonomous mode needs a dict of components
        components = {
            'climber': self.my_climber,
            'drive': self.my_drive,
            'feeder': self.my_feeder,
            #'shooter': self.my_shooter,
            'shooter_platform': self.my_shooter_platform,
            'target_detector': self.my_target_detector, 
        }

        self.components = [v for v in components.values()]
        self.autonomous_mode = AutonomousModeManager(components)
        
        
    def RobotInit(self):
        pass

    def Disabled(self):
        print("MyRobot::Disabled()")
    
        while self.IsDisabled():
            wpilib.Wait(control_loop_wait_time)
            
    def Autonomous(self):        
        print("MyRobot::Autonomous()")
        
        # this does all the autonomous mode work for us
        self.autonomous_mode.run(self, control_loop_wait_time)
        
    def OperatorControl(self):
        
        print("MyRobot::OperatorControl()")
        
        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExpiration(0.25)
        
        while self.IsOperatorControl():
            

            # 
            #    Driving
            #
            
            self.my_drive.drive(self.stick_axis(self.DRIVE_SPEED_AXIS),
                                self.stick_axis(self.DRIVE_ROTATE_AXIS),
                                self.stick_button_on(self.DRIVE_FASTER_BUTTON))
            
            #
            #    Climber
            #
            
            if self.stick_button_on(self.CLIMB_DOWN_BUTTON):
                self.my_climber.lower()
            elif self.stick_button_on(self.CLIMB_UP_BUTTON):
                self.my_climber.climb() 
            
            #
            #    Shooter
            #
            
            if self.is_toggle_on(self.MANUAL_SHOOTER_ON):
                self.my_shooter_platform.set_manual_speed(self.stick_axis(self.SHOOTER_WHEEL_AXIS))
            
            # TODO: automated platform angle stuff 
            if self.is_toggle_on(self.MANUAL_ANGLE_ON):
                self.my_shooter_platform.set_angle(self.stick_axis(self.PLATFORM_ANGLE_AXIS))
            
            #
            #    Feeder
            #
            
            if self.stick_button_on(self.FEEDER_FEED_BUTTON):
                self.my_feeder.feed()
            elif self.stick_button_on(self.FEEDER_BACK_BUTTON):
                self.my_feeder.feed_back()
            
            # calls update function on all components
            self.update()
            
            wpilib.Wait(control_loop_wait_time)
            dog.Feed()
    
    
    #
    #    Joystick utility functions (yay overhead!)
    #
    
    def is_toggle_on(self, channel):
        return self.eio.GetDigital(channel)
    
    def stick_axis(self, cfg):
        return self.ds.GetStickAxis(*cfg)
        
    def stick_button_on(self, cfg):
        return self.ds.GetStickButtons( cfg[0] ) & (1 << (cfg[1]-1))
    
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


