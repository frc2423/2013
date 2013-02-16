
try:
    import wpilib 
except ImportError:
    import fake_wpilib as wpilib
    

from autonomous import AutonomousModeManager
from common import *
from components import shooter_wheel, feeder, driving 
from systems import shooter
 

'''Declare all the ports and channels here'''
'''Note: these are shared between the electrical test and main code!'''

''' PWM channels'''
l_motor_pwm = 1
r_motor_pwm = 2

'''CAN channels'''
feeder_motor_can = 3
angle_motor_can = 4
shooter_motor_can = 7

'''Relay channels'''
camera_led_relay = 1
compressor_relay = 2

'''Analog channels'''
frisbee_sensor_channel = 3
feeder_sensor_channel = 4
shooter_sensor_channel = 5

''''Digital channels'''
compressor_switch = 1

'''Solenoids'''
valve1_channel = 1
valve2_channel = 2

'''All motors, sensors, and joysticks:'''

'''Joysticks'''
stick1 = wpilib.Joystick(1)
stick2 = wpilib.Joystick(2)

'''PWM Motors'''
l_motor = wpilib.Jaguar(l_motor_pwm)
r_motor = wpilib.Jaguar(r_motor_pwm)

'''CAN Motors'''
shooter_motor = wpilib.EzCANJaguar(shooter_motor_can)
shooter_motor.SetSpeedReference(wpilib.CANJaguar.kSpeedRef_QuadEncoder)
shooter_motor.ConfigEncoderCodesPerRev(360)
shooter_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)

angle_motor = wpilib.EzCANJaguar(angle_motor_can)
angle_motor.SetPositionReference(wpilib.CANJaguar.kPosRef_Potentiometer)
angle_motor.ConfigPotentiometerTurns(1)
angle_motor.ConfigNeutralMode(wpilib.CANJaguar.kNeutralMode_Brake)

feeder_motor = wpilib.EzCANJaguar(feeder_motor_can)

'''compressor for pneumatics'''
compressor = wpilib.Compressor(compressor_switch, compressor_relay)
compressor.Start()

'''solenoids for climber'''
'''TODO: should we use the DoubleSolenoid class instead?'''
valve1 = wpilib.Solenoid(valve1_channel)
valve2 = wpilib.Solenoid(valve2_channel)

'''sensors connected to jags: frisbee_sensor detects frisbees being held'''
frisbee_sensor = generic_distance_sensor.GenericDistanceSensor(frisbee_sensor_channel, generic_distance_sensor.GP2D120)
feeder_sensor = generic_distance_sensor.GenericDistanceSensor(feeder_sensor_channel, generic_distance_sensor.GP2D120)
shooter_sensor = generic_distance_sensor.GenericDistanceSensor(shooter_sensor_channel, generic_distance_sensor.GP2D120)

''' Variables:'''

'''motor positions'''
feed_motor_postion = feeder_motor_can.GetPosition()
angle_motor_position = angle_motor_can.GetPosition()
shooter_encoder_position = shooter_motor_can.GetPosition()
_
'''counting frisbees'''
frisbee_count = frisbee_sensor.Get()

'''Motor Speeds'''
feed_motor_spd = 1
shooter_motor_spd = 1

'''Loop time'''
control_loop_wait_time = 0.02

'''component constructor parameters'''
angle_threshold = 1 
speed_threshold = 1
driver = wpilib.RobotDrive()

'''TODO'''

                                                            
class MyRobot(wpilib.SimpleRobot):

    def __init__(self):
        wpilib.SimpleRobot.__init__(self)
        
        '''create the component instances'''
        self.my_shooter_wheel = shooter_wheel.ShooterWheel(angle_motor, shooter_motor,
                                                           angle_threshold, speed_threshold)
        self.my_feeder = feeder.Feeder(feeder_motor, frisbee_sensor, feeder_sensor)
        self.my_drive = driving.Driving(self.drive)
        
        '''create the system instance'''
        self.my_shooter = shooter.Shooter()
        
        '''autonomous mode needs a dict of components'''
        components = {
            'drive': self.my_drive,
            'feeder': self.my_feeder,
            'shooter': self.my_shooter,
            'shooter_wheel': self.my_shooter_wheel, }

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
        
        '''this does all the autonomous mode work for us'''
        self.autonomous_mode.run(self, control_loop_wait_time)
        
    def OperatorControl(self):
        print("MyRobot::OperatorControl()")
        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExperation(0.25)
        while self.IsOperatorControl():
            '''need a set_angle and set_speed function'''
            drive_speed = stick1.GetY() 
            drive_rotate = stick1.GetX() 
            speed = stick2.GetZ()
            self.my_drive.drive(drive_speed, drive_rotate)
            self.my_shooter.set_speed(speed)
            
            if stick2.GetTrigger():
                self.my_shooter.shoot_when_ready()
            
            '''calls update function on all components'''
            self.update()    
            
            self.wpilib.SmartDashboard.PutNumber('feed_motor', feed_motor_spd)
            self.wpilib.SmartDashboard.PutNumber('angle_motor', angle_motor_position)
            self.wpilib.SmartDashboard.PutNumber('frisbee_count', frisbee_count)
            self.wpilib.SmartDashboard.PutNumber('shooter_encoder', shooter_encoder_position)
            
            wpilib.Wait(control_loop_wait_time)
            dog.Feed()
           
                
    def update(self):
        '''Runs update on all components'''
        for component in self.components:
            component.update()
        

def run():
    robot = MyRobot()
    robot.StartCompetition()
    
    return robot


