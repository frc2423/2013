try:
    import wpilib
except:
    import fake_wpilib as wpilib





''' distances at which we think we detect different amount of frisbees '''
ONE_FRISBEE = 9
TWO_FRISBEE = 7
THREE_FRISBEE = 5
FOUR_FRISBEE = 2
FEEDER_READY_DISTANCE = 2

FrisbeeCount = "Frisbee Count"

#State variables
FEEDING = 0
STOP_FEEDING = 1
STOP = 2
MANUAL = 3
AUTO = 4
REVERSE = 5
START_FEEDING = 6

#Speed variables
REVERSE_FEED_SPEED = -1
FEED_SPEED = 1
ZERO = 0

#Modes
BACKWARDS = 0
FORWARDS = 1

class Feeder():
    
    '''Contains all the functions that control the cam motor'''

    def __init__(self, feed_motor, frisbee_sensor, feed_sensor, frisbee_sensor_switch):
        
        '''saves all the variables, sets the state, and sets the motor speed to zero'''
        self.feed_motor = feed_motor
        self.frisbee_sensor = frisbee_sensor
        self.feed_sensor = feed_sensor
        self.frisbee_sensor_switch = frisbee_sensor_switch
        self.FEEDING_motor.Set(ZERO)
        self.state = None
        self.state = STOP_FEEDING
        self.distance = self.frisbee_sensor.GetDistance()
        self.fed = 1
        
        
        
        
        
    def auto_feed(self): 
        '''if the cam is not on the sensor, move the cam. 
        If it is  and has just feed stop. 
        If it was not feeding and the cam is on the sensor start moving'''
        
        self.state = AUTO
       
        
    def manual(self):
        '''manual motor control'''
        self.state = MANUAL
        
        
    def reverse_feed(self):
        '''makes the cam reverse'''
        
        self.state = REVERSE
        
    def is_sensor_working(self):
        if self.frisbee_sensor_switch == True:
            return True
        
        elif self.frisbee_sensor_switch == False:
            return False
        
    def get_frisbee_count(self):
        
        if self.is_sensor_working(self) == False:
            self.frisbee_count = 1
            
        else:
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
    def update(self):
        '''sets all the Jaguars'''
            
        if self.state == REVERSE:
            
            self.mode = BACKWARDS
            self.state= FEEDING
            
        if self.state == MANUAL:
            
            self.state = FEEDING
            self.mode = FORWARDS
            
        if self.state == AUTO:
            '''if the cam is not on the sensor, move the cam. 
            If it is  and has just FEEDING stop. 
            If it was not FEEDINGing and the cam is on the sensor start moving'''
        
            #there is no cam above the sensor
            if self.feed_sensor.GetDistance() > FEEDER_READY_DISTANCE:
            
                self.state = FEEDING
                self.mode = FORWARDS
            
            #there is a cam above the sensor and it was feeding
            elif self.feed_sensor.GetDistance() <= FEEDER_READY_DISTANCE and \
                self.state == FEEDING:
            
                self.state = STOP_FEEDING
                
            #there is a cam above the sensor and it was not feeding
            elif self.feed_sensor.GetDistance() <= FEEDER_READY_DISTANCE and \
                self.state == STOP_FEEDING:
                
                self.state = FEEDING
                self.mode = FORWARDS
                
        if self.state == FEEDING:
            self.state = START_FEEDING        
                
        if self.state == START_FEEDING:
            
            if self.mode == FORWARDS:
            
                self.feed_motor.Set(FEED_SPEED)
                
                
            elif self.mode == BACKWARDS:
                
                self.feed_motor.Set(REVERSE_FEED_SPEED)
                
        if self.state == STOP_FEEDING:
            self.state = STOP
        
            
        if self.state == STOP:
            self.FEEDING_motor.Set(ZERO)
                