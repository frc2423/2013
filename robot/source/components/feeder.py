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
state = STATE_FEED
class Feeder():

    def __init__(self, feed_motor, frisbee_sensor, feed_sensor):
        self.feed_motor = feed_motor
        self.frisbee_sensor = frisbee_sensor
        self.feed_sensor = feed_sensor
        self.feed_motor.Set(INITIAL_SPD)
        self.updated = None
        self.FEEDER_READY_DISTANCE = 2   
        self.state = STATE_FEED
    
    def feed(self):
        '''makes the feed motor go 1 full rotation then stops'''
        if self.feed_sensor.GetDistance() >= 0 and \
            self.feed_sensor.GetDistance() < FEEDER_READY_DISTANCE and \
            self.state == STATE_FEED:
            
            self.updated = True
            
        if self.feed_sensor.GetDistance() >= FEEDER_READY_DISTANCE and self.state == STATE_READY:
            self.updated = False
            
        if self.feed_sensor.GetDistance() >= FEEDER_READY_DISTANCE:
            frisbee_fed = True
            
    def get_frisbee_count(self):
        '''Gets the distance away an object is from the sensor based on the voltage of the sensor'''
        
        if self.frisbee_sensor.GetDistance() == ONE_FRISBEE:
            frisbee_count = 1
            return 1
        
        elif self.frisbee_sensor.GetDistance() == TWO_FRISBEE:
            frisbee_count = 2
            return 2
        
        elif self.frisbee_sensor.GetDistance() == THREE_FRISBEE:
            frisbee_count = 3
            return 3
        
        elif self.frisbee_sensor.GetDistance() == FOUR_FRISBEE:
            frisbee_count = 4
            return 4
        
        else:
            frisbee_count = 0
            return 0
        wpilib.SmartDashboard.PutNumber(FrisbeeCount, frisbee_count)

    def update(self):
        
        if self.updated == True:
            self.feed_motor.Set(FEED_SPD)
            self.state = STATE_READY
            self.updated = None
            
        if self.updated == False:
            self.feed_motor.Set(INITIAL_SPD)
            self.updated = None
            self.state = STATE_FEED