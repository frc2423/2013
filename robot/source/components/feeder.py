try:
    import wpilib
except:
    import fake_wpilib as wpilib


#
#Motor Speeds
#
'''Feeder motor polarity switched, so the motor ran backwards'''
STOP_SPEED = 0
FEED_SPEED = 0.7
REVERSE_SPEED = -1
#
#Frisbee Distances
#
ONE_FRISBEE = 5.8
TWO_FRISBEE = 4.7
THREE_FRISBEE = 3.9
FOUR_FRISBEE = 3.2
FIVE_FRISBEE = 2.7
SIX_FRISBEE = 2.0
FEEDER_READY_DISTANCE = 2.15

#
#SmartDashboard String
#
DASH_STRING_FRISBEE = "Frisbee Count"

#
# Feeder States: what the motor is actually doing
#
STATE_FEEDING = 0
STATE_REVERSING = 1
STATE_STOPPED = 2
STATE_FEEDING_AUTO_BEGIN = 3
STATE_FEEDING_AUTO_NO_STOP = 4
STATE_FEEDING_AUTO_STOP_ON_SENSOR = 5


#
# Action States: what the user wants
#
ACT_STATE_FEED = 0
ACT_STATE_FEED_AUTO = 1
ACT_STATE_REVERSE = 2
ACT_STATE_STOP =3

#
#Timer
#
FEEDER_WAIT_TIME = .25

class Feeder():
    
    '''Contains all the functions that control the cam motor'''

    def __init__(self, feed_motor, frisbee_sensor, feed_sensor):
        
        '''
            Initializes Feeder class
                
            param:feed_motor - EzCANJaguar set for kPercentVbus
            param:frisbee_sensor - GP2D120 distance sensor
            param:feed_sensor - GP2D120 distance sensor
        '''

        self.feed_motor = feed_motor
        self.frisbee_sensor = frisbee_sensor
        self.feed_sensor = feed_sensor
        self.feed_motor.Set(STOP_SPEED)
        
        self.feeder_state = STATE_STOPPED
        self.action_state = ACT_STATE_STOP
        self.distance = self.frisbee_sensor.GetDistance()
        self.using_frisbee_sensor = True
        
        #mode of which feed to use
        self.feed_mode_auto = True
        
        self.sd_frisbees = 20
        self.wait_timer = wpilib.Timer()
        
        self.stop = False
        
    def get_frisbee_count(self):    
        '''Gets the distance away an object is from the sensor based on the voltage of the sensor'''
        self.frisbee_count = None
        
        if self.using_frisbee_sensor == True:
            
            self.distance = self.frisbee_sensor.GetDistance()
            
            if self.distance <= ONE_FRISBEE and self.distance >= TWO_FRISBEE:
                self.frisbee_count = 1
            
            elif self.distance <= TWO_FRISBEE and self.distance >= THREE_FRISBEE:
                self.frisbee_count = 2
            
            elif self.distance <= THREE_FRISBEE and self.distance >= FOUR_FRISBEE:
                self.frisbee_count = 3
    
            elif self.distance <= FOUR_FRISBEE and self.distance >= FIVE_FRISBEE:
                self.frisbee_count = 4
                
            elif self.distance <= FIVE_FRISBEE and self.distance >= SIX_FRISBEE:
                self.frisbee_count = 5
           
            elif self.distance > ONE_FRISBEE:
                self.frisbee_count = 0
            
        return self.frisbee_count
    
    def has_frisbee(self):
        return self.get_frisbee_count() != 0
        
    def use_frisbee_sensor(self, using_frisbee_sensor):
        self.using_frisbee_sensor = using_frisbee_sensor
        
    def sensor_covered(self):
        '''
            checks if the kicker is covering the sensor
        '''
        return self.feed_sensor.GetDistance() < FEEDER_READY_DISTANCE
    
    def set_auto_mode(self, value):
        ''' sets mode auto '''
        self.feed_mode_auto = bool(value)
         
    def feed(self):
        ''' determines feed mode and uses it '''
        if self.feed_mode_auto:
            self.feed_auto()
        else:
            self.feed_manual()
            
    def feed_auto(self):
        ''' 
            automatic feed function this will stop at the sensor location
            This should not be used externally use feed() instead
        '''
        
        #
        #Kicker is not feeding automatically feed!
        #        
        self.action_state = ACT_STATE_FEED_AUTO
          
    def feed_manual(self):
        ''' feeds while called '''
        self.action_state = ACT_STATE_FEED
        
    def reverse_feed(self):
        ''' reverses the feeder manually'''
        self.action_state = ACT_STATE_REVERSE
        
    def update(self):
        ''' Sets actual motor values based on states '''
    
        #
        # Process the user actions first
        # -> Note that all of the user actions have a stop after them
        #
        
        if self.action_state == ACT_STATE_FEED:
            self.feeder_state = STATE_FEEDING

        elif self.action_state == ACT_STATE_FEED_AUTO:
            # only change the feeder state if it is currently stopped
            if self.feeder_state == STATE_STOPPED:
                self.feeder_state = STATE_FEEDING_AUTO_BEGIN
            
        elif self.action_state == ACT_STATE_REVERSE:
            self.feeder_state = STATE_REVERSING
            
        # if the user doesn't tell us to do anything else, stop
        self.action_state = ACT_STATE_STOP
        
        #
        # Process the feeder states next
        # -> These actually touch the feeder motors
        #
            
        if self.feeder_state == STATE_FEEDING:
            self.feed_motor.Set(STOP_SPEED)
            self.feeder_state = STATE_STOPPED
            
        elif self.feeder_state == STATE_REVERSING:
            self.feed_motor.Set(STOP_SPEED)
            self.feeder_state = STATE_STOPPED
            
        elif self.feeder_state == STATE_STOPPED:
            self.feed_motor.Set(STOP_SPEED)
            self.feeder_state = STATE_STOPPED
            
        elif self.feeder_state == STATE_FEEDING_AUTO_BEGIN:
            self.feed_motor.Set(FEED_SPEED)
            self.feeder_state = STATE_FEEDING_AUTO_NO_STOP
            
            # initialize the next state's timer
            self.wait_timer.Reset()
            self.wait_timer.Start()
            
        elif self.feeder_state == STATE_FEEDING_AUTO_NO_STOP:
            self.feed_motor.Set(FEED_SPEED)
            
            # only stay in this state for FEEDER_WAIT_TIME, then move to the next state
            if self.wait_timer.HasPeriodPassed(FEEDER_WAIT_TIME):
                self.feeder_state = STATE_FEEDING_AUTO_STOP_ON_SENSOR
            
        elif self.feeder_state == STATE_FEEDING_AUTO_STOP_ON_SENSOR:
            if self.sensor_covered():
                self.feed_motor.Set(STOP_SPEED)
                self.feeder_state = STATE_STOPPED
            else:
                self.feed_motor.Set(FEED_SPEED)
        
        
        #print("Feeder", self.feeder_state, self.action_state)
        #wpilib.SmartDashboard.PutNumber('Feeder State', self.feeder_state)
        #wpilib.SmartDashboard.PutNumber('Action State', self.action_state)
        wpilib.SmartDashboard.PutNumber('Feeder dist', self.feed_sensor.GetDistance())
        wpilib.SmartDashboard.PutBoolean('Feeder covered', self.sensor_covered())
    
    
        fs = self.get_frisbee_count()
        if self.frisbee_count is None:
            fs = -1
            
        if fs != self.sd_frisbees:
            wpilib.SmartDashboard.PutNumber('Frisbees', fs)
            self.sd_frisbees = fs
            
        #wpilib.SmartDashboard.PutNumber('Frisbee Distance', self.distance)
        
