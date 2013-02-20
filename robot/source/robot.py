
try:
    import wpilib 
except ImportError:
    import fake_wpilib as wpilib
    

from autonomous import AutonomousModeManager

from common.auto_jaguar import AnglePositionJaguar, SpeedJaguar
#from common.bang_bang_jaguar import BangBangJaguar
from common.ez_can_jaguar import EzCANJaguar
from common.generic_distance_sensor import GenericDistanceSensor, GP2D120

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
control_loop_wait_time = 0.02


                                                            
class MyRobot(wpilib.SimpleRobot):
    
    # available toggle switch ports on enhanced EIO
    # -> 2, 4, 8, 12, 16
    
    # import into this namespace
    ANGLE_MIN_ANGLE = ANGLE_MIN_ANGLE
    ANGLE_MAX_ANGLE = ANGLE_MAX_ANGLE
    
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
    ANGLE_POINT_AXIS    = (1, Z)
    
    SHOOTER_WHEEL_AXIS  = (2, Z)
    PLATFORM_ANGLE_AXIS = (2, Y)
    
    # button definitions -- (stick number, button number)
    # -> call stick_button_on() with this value to get True/False
    
    DRIVE_FASTER_BUTTON     = (1, TOP)
    
    CLIMB_TWIST_L_BUTTON    = (1, 8)
    CLIMB_TWIST_R_BUTTON    = (1, 9)
    
    CLIMB_UP_BUTTON         = (2, 10)
    CLIMB_DOWN_BUTTON       = (2, 11)
    
    FEEDER_FEED_BUTTON      = (2, TRIGGER)
    FEEDER_BACK_BUTTON      = (2, TOP)
    
    AUTO_TARGET_BUTTON      = (1, TRIGGER)
    
    # toggle switch definitions
    # -> call is_toggle_on() with this value to get True/False
    
    SHOOTER_ON              = EIO_CHANNELS[0]
    MANUAL_SHOOTER_ON       = EIO_CHANNELS[1]
    MANUAL_ANGLE_ON         = EIO_CHANNELS[2]
    AUTO_TARGETING_ON       = EIO_CHANNELS[3]
    
    
    def __init__(self):
        wpilib.SimpleRobot.__init__(self)
        
        self.ds = wpilib.DriverStation.GetInstance()
        self.eio = self.ds.GetEnhancedIO()
        
        # initialize the enhanced I/O ports for toggle switches
        
        for channel in self.EIO_CHANNELS:
            self.eio.SetDigitalConfig(channel, wpilib.DriverStationEnhancedIO.kInputFloating)
        
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
        # self.autonomous_mode = AutonomousModeManager(components)
        
    
        
    def RobotInit(self):
        pass

    def Disabled(self):
        print("MyRobot::Disabled()")
    
        while self.IsDisabled():
            wpilib.Wait(control_loop_wait_time)
            
    def Autonomous(self):        
        print("MyRobot::Autonomous()")
        
        # put this in a consistent state when starting the robot
        self.my_climber.lower()
        
        # this does all the autonomous mode work for us
        # self.autonomous_mode.run(self, control_loop_wait_time)
        
    def OperatorControl(self):
        
        print("MyRobot::OperatorControl()")
        
        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExpiration(0.25)
        
        # put this in a consistent state when starting the robot
        self.my_climber.lower()
        compressor.Start()
        
        #wpilib.SmartDashboard.PutNumber('Angle P', ANGLE_P)
        #wpilib.SmartDashboard.PutNumber('Angle I', ANGLE_I)
        #wpilib.SmartDashboard.PutNumber('Angle D', ANGLE_D)
        
        #wpilib.SmartDashboard.PutNumber('Shooter P', SHOOTER_P)
        #wpilib.SmartDashboard.PutNumber('Shooter I', SHOOTER_I)
        #wpilib.SmartDashboard.PutNumber('Shooter D', SHOOTER_D)
        
        while self.IsOperatorControl() and self.IsEnabled():
            
            # measure loop time
            start = wpilib.Timer.GetPPCTimestamp()
            

            # 
            #    Driving
            #
            
            self.my_drive.drive(self.stick_axis(self.DRIVE_SPEED_AXIS),
                                self.stick_axis(self.DRIVE_ROTATE_AXIS),
                                self.stick_button_on(self.DRIVE_FASTER_BUTTON))
            
            #
            #    Shooter
            #
            
            shootery = self.translate_axis(self.SHOOTER_WHEEL_AXIS, -1.0, 0.0)
            wpilib.SmartDashboard.PutNumber('Shooter Raw', shootery)
            
            if self.is_toggle_on(self.SHOOTER_ON):
                #if self.is_toggle_on(self.MANUAL_SHOOTER_ON):
                
                self.my_shooter_platform.set_speed_manual(shootery)
                #else:
                #    z = self.translate_axis(self.SHOOTER_WHEEL_AXIS, 1000.0, 0)
                #    self.my_shooter_platform.set_speed_auto(z)
            else:
                self.my_shooter_platform.set_speed_manual(0.0)
                #shooter_motor.SetPID( wpilib.SmartDashboard.GetNumber('Shooter P'),
                #                      wpilib.SmartDashboard.GetNumber('Shooter I'),
                #                      wpilib.SmartDashboard.GetNumber('Shooter D'))
            
            #
            #    Angle
            #        
             
            if not self.is_toggle_on(self.MANUAL_ANGLE_ON):
                angle_z = self.translate_axis(self.ANGLE_POINT_AXIS, self.ANGLE_MIN_ANGLE, self.ANGLE_MAX_ANGLE)
                self.my_shooter_platform.set_angle_auto(angle_z)
            else:
                self.my_shooter_platform.set_angle_manual(-self.stick_axis(self.PLATFORM_ANGLE_AXIS))
                
                #angle_motor.SetPID( wpilib.SmartDashboard.GetNumber('Angle P'),
                #                    wpilib.SmartDashboard.GetNumber('Angle I'),
                #                    wpilib.SmartDashboard.GetNumber('Angle D'))
            
            #
            #    Feeder
            #
            
            if self.stick_button_on(self.FEEDER_FEED_BUTTON):
                self.my_feeder.feed_auto()
            elif self.stick_button_on(self.FEEDER_BACK_BUTTON):
                self.my_feeder.reverse_feed()
                
            #
            #     Auto targeting
            #
            
            # TODO: figure out how to activate this properly?
            # -> perhaps enable the mode, have the driver enable steering?
            if self.is_toggle_on(self.AUTO_TARGETING_ON):
                self.my_auto_targeting.perform_targeting()
                
                if self.stick_button_on(self.AUTO_TARGET_BUTTON):
                    self.my_robot_turner.auto_turn()
                
            #
            #    Climber
            #        - Must come after anything that sets angle, otherwise
            #        the climbing safety features won't kick in
            #
            
            if self.stick_button_on(self.CLIMB_DOWN_BUTTON):
                self.my_climber.lower()
            elif self.stick_button_on(self.CLIMB_UP_BUTTON):
                self.my_climber.climb() 
            
            if self.stick_button_on(self.CLIMB_TWIST_L_BUTTON):
                self.my_drive.drive(0.0, -0.9)
            elif self.stick_button_on(self.CLIMB_TWIST_R_BUTTON):
                self.my_drive.drive(0.0, 0.9)         
            
            #
            # Update phase, actually sets motors and stuff
            #
            
            self.update()
            
            # how long does it take us to run the loop?
            # -> we're using a lot of globals, what happens when we change it?
            wpilib.SmartDashboard.PutNumber('Loop time', wpilib.Timer.GetPPCTimestamp() - start)
            
            wpilib.Wait(control_loop_wait_time)
            dog.Feed()
            
        compressor.Stop()
    
    #
    #    Joystick utility functions (yay overhead!)
    #
    
    def is_toggle_on(self, channel):
        return not self.eio.GetDigital(channel)
    
    def stick_axis(self, cfg):
        return self.ds.GetStickAxis(*cfg)
    
    def translate_axis(self, cfg, amin, amax):
        '''Returns an axis value between a min and a max'''
        a = self.ds.GetStickAxis(*cfg)
        
        # Xmax - (Ymax - Y)( (Xmax - Xmin) / (Ymax - Ymin) )
        return amax - ((1 - a)*( (amax - amin) / 2.0 ) )
        
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


