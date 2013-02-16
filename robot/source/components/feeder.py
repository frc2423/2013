try:
    import wpilib
except:
    import fake_wpilib as wpilib



INITIAL_SPD = 0
FEED_SPD = 1

''' distances at which we think we detect different amount of frisbees '''
ONE_FRISBEE = 9
TWO_FRISBEE = 7
THREE_FRISBEE = 5
FOUR_FRISBEE = 2
FEEDER_READY_DISTANCE = 2

FrisbeeCount = "Frisbee Count"
STATE_FEED = 0
STATE_READY = 1
reset = 2
class Feeder():
    
    '''Contains all the functions that control the cam motor'''

    def __init__(self, feed_motor, frisbee_sensor, feed_sensor):
        
        '''saves all the variables, sets the state and sets FEEDER_READY_DISTANCE'''
        self.feed_motor = feed_motor
        self.frisbee_sensor = frisbee_sensor
        self.feed_sensor = feed_sensor
        self.feed_motor.Set(INITIAL_SPD)
        self.updated = None
        self.state = STATE_READY
        self.FEEDER_READY_DISTANCE = 2
        self.distance = self.frisbee_sensor.GetDistance()
    
    def feed(self):
        
        '''feeds the frisbee'''
        
        if self.feed_sensor.GetDistance() > FEEDER_READY_DISTANCE and \
            self.state == STATE_FEED:
            
            self.state = STATE_FEED
            self.updated = True
            print("State is : ", 1)  
            
        elif self.feed_sensor.GetDistance() <= FEEDER_READY_DISTANCE and \
            self.state == STATE_FEED:
            
            self.updated = reset
            print("State is : ", 2)
            
        elif self.feed_sensor.GetDistance() <= FEEDER_READY_DISTANCE and \
            self.state == STATE_READY:
            
            self.state = STATE_FEED
            self.updated = True
            print("State is : ", 3)
            
        elif self.frisbee_sensor.GetDistance() > FEEDER_READY_DISTANCE and \
            self.state == STATE_READY:   
            
            self.state = 2
            self.state = None
            self.updated = False
            print("State is : ", 4)
        
        self.run_once = True
        print("Frisbee Distance Is: ", self.feed_sensor.GetDistance())
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
        '''Gets the self.self.distance away an object is from the sensor based on the voltage of the sensor'''
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
    def update(self):
        '''sets all the Jaguars'''
        
        if self.updated == True:
            self.feed_motor.Set(FEED_SPD)
            self.updated = None
            
            
        if self.updated == 1:
            self.feed_motor.Set(FEED_SPD)
            self.updated = None
            
            
        if self.updated == False:
            self.feed_motor.Set(INITIAL_SPD)
            self.updated = None
            
            
        
            self.state = 0
        print("Feed speed is: ", self.feed_motor.value)
