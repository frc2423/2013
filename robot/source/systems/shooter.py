try:
    import wpilib
except:
    import fake_wpilib as wpilib

SHOOT_TIME = .5
class Shooter():
    '''
        shooter class which controls the interactions of the feeder and the 
        shooter_platform 
    '''
    
    def __init__(self, shooter_platfrom, feeder, driver = None):
        '''
            Initializes shooter class
            
            param:shooter_platform - a shooter_platform object, all setup
            param:feeder - a feeder object all setup
        '''
    
        self.shooter_platform = shooter_platfrom
        self.feeder = feeder
        self.driver = driver
        self.state = None
        self.min_calls = wpilib.Timer
        self.manual_feed = False
    
    def shoot_if_ready(self):
        ''' if motor is ready and there are frisbees set feeder to kick frisbee '''
        self.feeder.set_auto_mode(True)
        
        # TODO: Fix this
        
        if self.shooter_platform.is_ready()  and self.feeder.has_frisbee():
            #auto feed when in auto mode
            self.feeder.feed_auto()
                
        elif self.shooter_platform.is_ready() and self.manual_feed:
            if self.min_calls.Get() == 0:
                self.min_calls.Start()
                self.feeder.feed()
                self.manual_feed = True
                
            elif not self.min_calls.HasPeriodPassed(SHOOT_TIME):            
                self.feeder.feed()
            
            else:
                self.min_calls.Stop()
                self.min_calls.Reset()
                self.manual_feed = False
                
    # no update function required