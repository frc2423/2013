try:
    import wpilib
except:
    import fake_wpilib as wpilib


#
#Motor Speeds
#
STOP_SPEED = 0
FEED_SPEED = 1

#
#Frisbee Distances
#
ONE_FRISBEE = 9
TWO_FRISBEE = 7
THREE_FRISBEE = 5
FOUR_FRISBEE = 2
FEEDER_READY_DISTANCE = 2

#
#SmartDashboard String
#
DASH_STRING_FRISBEE = "Frisbee Count"

#
#Feeder States
#
ACT_STATE_FEEDING = 0
STATE_STOPPED = 1
STATE_REVERSING = 2
ACT_STATE_FEEDING_AUTO = 3


#
#Action States
#
ACT_STATE_FEED = 0
ACT_STATE_FEED_AUTO =1
ACT_STATE_REVERSE = 2

class FeederPro():
    
    '''Contains all the functions that control the cam motor'''

    def __init__(self, feed_motor, frisbee_sensor, feed_sensor):
        
        '''
            Initializes FeederPro class
                
            param:feed_motor - EzCANJaguar set for kPercentVbus
            param:frisbee_sensor - GP2D120 distance sensor
            param:feed_sensor - GP2D120 distance sensor
        '''

        self.feed_motor = feed_motor
        self.frisbee_sensor = frisbee_sensor
        self.feed_sensor = feed_sensor
        self.feed_motor.Set(STOP_SPEED)
        self.updated = None
        self.state_feeder = STATE_STOPPED
        self.state_action = None
        self.distance = self.frisbee_sensor.GetDistance()

        
    def get_frisbee_count(self):    
        '''Gets the distance away an object is from the sensor based on the voltage of the sensor'''
        self.frisbee_count = None
        self.distance = self.frisbee_sensor.GetDistance()
        
        if self.distance <= ONE_FRISBEE and self.distance >= TWO_FRISBEE:
            self.frisbee_count = 1
        
        elif self.distance <= TWO_FRISBEE and self.distance >= THREE_FRISBEE:
            self.frisbee_count = 2
        
        elif self.distance <= THREE_FRISBEE and self.distance >= FOUR_FRISBEE:
            self.frisbee_count = 3

        elif self.distance <= FOUR_FRISBEE and self.distance > 1:
            self.frisbee_count = 4
       
        elif self.distance > ONE_FRISBEE:
            self.frisbee_count = 0
            
        return self.frisbee_count
    
    def sensor_covered(self):
        '''
            checks if the kicker is covering the sensor
        '''
        return self.feed_sensor.GetDistance < FEEDER_READY_DISTANCE
    
    def feed_auto(self):
        ''' automatic feed function this will stop at the sensor location'''
        
        #
        #Kicker is not feeding automatically feed!
        #        
        if self.state_feeder != ACT_STATE_FEED_AUTO:
            self.state_action = ACT_STATE_FEED_AUTO
          
    def feed_man(self):
        ''' feeds while called '''
        self.state_action = ACT_STATE_FEED
        
    def update(self):
        ''' Sets actual motor values based on states '''
    
            
        #
        #if sensor is covered, stop feeding
        #
        if self.state_feeder == ACT_STATE_FEEDING and sensor_covered():
            
            self.feed_motor.Set(STOP_SPEED)
            self.state_feeder = STATE_STOPPED
        
        #
        #we were told to feed so lets!
        #
        if self.action_state == ACT_STATE_FEED:
            
            self.feed_motor.Set(FEED_SPEED)
            self.state_feeder = ACT_STATE_FEEDING
            self.state_action = None
            
    
        if self.action_state = ACT
        
