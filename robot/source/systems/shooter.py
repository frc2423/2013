from components import shooter_platform
from components import feeder

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
    
        self.shooter_platform = shooter_platform
        self.feeder = feeder
        self.driver = driver
        self.state = None
    
    def shoot_if_ready(self):
        ''' if motor is ready and there are frisbees set feeder to kick frisbee '''
        if  self.shooter_platform.is_ready()  and \
            self.feeder.has_frisbee():
            feeder.feed_auto()
        
    # no update function required