try:
    import wpilib
except:
    import fake_wpilib as wpilib



INITIAL_SPD = 0
FEED_SPD = 1
ZERO_FRISBEE = 0
ONE_FRISBEE = 1
TWO_FRISBEE = 2
THREE_FRISBEE = 3
FOUR_FRISBEE = 4
FEEDER_READY_DISTANCE = 2
   
FrisbeeCount = "Frisbee Count"

STATE_FEED = 0
STATE_READY = 1

class Feeder():

    def __init__(self, feed_motor, frisbee_sensor, feed_sensor):
        self.feed_motor = feed_motor
        self.frisbee_sensor = frisbee_sensor
        self.feed_sensor = feed_sensor
        self.feed_motor.Set(INITIAL_SPD)
        self.updated = None
        self.state = STATE_READY
        self.FEEDER_READY_DISTANCE = 2   
        
    
    def feed(self):
        
        if self.feed_sensor.GetDistance() > FEEDER_READY_DISTANCE and \
            self.state = STATE_READY:
            
            self.updated = False
            self.state = STATE_FEED
            
        if self.feed_sensor.GetDistance() <= FEEDER_READY_DISTANCE and \
            self.state == STATE_FEED:
            
            self.updated = 1
            self.state = STATE_READY   
    
    def feed_when_ready(self):
        '''makes the feed motor go 1 full rotation then stops'''
        if feed_sensor.GetDistance() > FEEDER_READY_DISTANCE:  
            self.updated = False
            
        if self.state == STATE_FEED and \
            self.feed_sensor.GetDistance() <= FEEDER_READY_DISTANCE:
            self.updated = True    
            
    def ready_feeder(self):
         '''Rotates the cam until it is above the sensor'''
         
         if self.state == STATE_READY:
            self.updated = True
            self.state = STATE_FEED
            
        if self.state == STATE_READY and \
            self.feed_sensor.GetDistance() <= FEEDER_READY_DISTANCE:
            self.updated = False
            self.state = STATE_FEED
            
    def get_frisbee_count(self):
        '''Gets the distance away an object is from the sensor based on the voltage of the sensor'''
        
        if self.frisbee_sensor.GetDistance() == ONE_FRISBEE:
            frisbee_count = 1
        
        elif self.frisbee_sensor.GetDistance() == TWO_FRISBEE:
            frisbee_count = 2
        
        elif self.frisbee_sensor.GetDistance() == THREE_FRISBEE:
            frisbee_count = 3

        elif self.frisbee_sensor.GetDistance() == FOUR_FRISBEE:
            frisbee_count = 4
       
        else:
            frisbee_count = 0
        
        wpilib.SmartDashboard.PutNumber(FrisbeeCount, frisbee_count)
        return frisbee_count
    
    def update(self):
        
        print(self.state)
        
        if self.updated == True and get_frisbee_count > 0:
            self.feed_motor.Set(FEED_SPD)
            self.updated = None
            
        if self.updated == 1:
            self.feed_motor.Set(FEED_SPD)
       
        if self.updated == False:
            self.feed_motor.Set(INITIAL_SPD)
            
            