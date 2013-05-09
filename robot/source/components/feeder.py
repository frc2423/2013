try:
    import wpilib
except:
    import fake_wpilib as wpilib


#
#Motor Speeds
#
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
#Feeder States
#
STATE_FEEDING = 0
STATE_FEEDING_AUTO = 1
STATE_REVERSING = 2
STATE_STOPPED = 3


#
#Action States
#
ACT_STATE_FEED = 0
ACT_STATE_FEED_AUTO = 1
ACT_STATE_REVERSE = 2
ACT_STATE_STOP =3

#
#Timer
#
FEEDER_WAIT_TIME = .5

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
		
        self.timer = wpilib.Timer()
        
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
        #Feed actions
        #

        
        #
        #we were told to feed so lets!
        #
        if self.action_state == ACT_STATE_FEED:
            
            self.feed_motor.Set(FEED_SPEED)
            self.feeder_state = STATE_FEEDING
            #if feed is not called in next loop then stop the motor!
            self.action_state = ACT_STATE_STOP
            
        elif self.action_state == ACT_STATE_FEED_AUTO:
            self.feed_motor.Set(FEED_SPEED)
            self.feeder_state = STATE_FEEDING_AUTO
            self.action_state = ACT_STATE_STOP
            self.stop = False
            self.timer.Start()
        #
        #Feeder in auto feeding, and sensor isn't covered, keep feeding
        #
        elif self.feeder_state == STATE_FEEDING_AUTO and not self.sensor_covered():
            self.feed_motor.Set(FEED_SPEED)
			
        elif self.feeder_state == STATE_FEEDING_AUTO and self.sensor_covered() and self.stop == False:
            self.feed_motor.Set(FEED_SPEED)
		
        #
        #Reverse the feeder
        #
        elif self.action_state == ACT_STATE_REVERSE:
            self.feed_motor.Set(REVERSE_SPEED)
            self.feeder_state = STATE_REVERSING
            #if feed is not called in next loop then stop the motor!
            self.action_state = ACT_STATE_STOP
      
        
        #
        #Stop actions
        #
        
        #
        #if sensor is covered, stop feeding
        #
        elif self.feeder_state == STATE_FEEDING_AUTO and self.sensor_covered():

            
            self.feed_motor.Set(STOP_SPEED)
            self.feeder_state = STATE_STOPPED    
            
        #
        #we weren't told to feed so stop!
        #
        elif self.action_state == ACT_STATE_STOP and self.timer.Get() > FEEDER_WAIT_TIME:
            
            self.feed_motor.Set(STOP_SPEED)
            self.feeder_state = STATE_STOPPED
            self.stop = True
            self.timer.Stop()
            self.timer.Reset()
    
        
        #wpilib.SmartDashboard.PutNumber('Feeder State', self.feeder_state)
        #wpilib.SmartDashboard.PutNumber('Action State', self.action_state)
        #wpilib.SmartDashboard.PutNumber('Feeder dist', self.feed_sensor.GetDistance())
    
        fs = self.get_frisbee_count()
        if self.frisbee_count is None:
            fs = -1
            
        if fs != self.sd_frisbees:
            wpilib.SmartDashboard.PutNumber('Frisbees', fs)
            self.sd_frisbees = fs
            
        #wpilib.SmartDashboard.PutNumber('Frisbee Distance', self.distance)
        
