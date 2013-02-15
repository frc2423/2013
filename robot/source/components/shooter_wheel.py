try:
    import wpilib
except ImportError: 
    import fake_wpilib as wpilib
    

class ShooterWheel(object):
    ''' checks if it is ready to shoot (angle and speed) and if not, sets those values'''
    
    def __init__(self, angle_jag, shooter_jag, angle_threshold, speed_threshold):
        ''' stores each jaguar and threshold value with the instance'''
        self.updated = False
        self.angle_jag = angle_jag
        self.shooter_jag = shooter_jag
        self.angle_threshold = angle_threshold
        self.speed_threshold = speed_threshold
       
    def current_angle(self):
        ''' Gets the angle and is reused'''
        return self.angle_jag.GetPosition()   
    
    def current_speed(self):
        ''' Gets the speed and is reused'''
        return self.shooter_jag.GetSpeed()
     
    def set_angle(self, d_angle):
        '''sets the angle to the d_angle'''
        self.updated = True
        self.d_angle = d_angle
        #stores the past parameter w/ the instance
    
    def set_speed(self, d_speed):
        '''sets the speed to the d_speed'''
        self.updated = True
        self.d_speed = d_speed
        #Stores the past parameter w/ the instance
        
    def stop(self):
        ''' stops each jag when needed '''
        self.updated = True
        self.d_angle = 0
        self.d_speed = 0
        #sets the two motors to stop when called
        
    def is_ready_angle(self, d_angle):
        ''' checks if the angle is right''' 
        if self.current_angle() >= (self.d_angle - self.angle_threshold) and self.current_angle() <= (self.d_angle + self.angle_threshold):
            return True
            
        else:
            return False
        #returns true if current angle is within threshold.
        
   
    def is_ready_speed(self, d_speed):
        ''' checks if the speed is right'''
        if self.current_speed() >= (self.d_speed - self.speed_threshold) and self.current_speed() <= (self.d_speed + self.speed_threshold):
            return True

        else:
            return False
        #returns true if current speed is within threshold.
        
    def is_ready(self):
        ''' checks if the shooter_wheel is ready to shoot'''
        print ('self.d_angle =', self.d_angle)
        print ('self.d_speed =', self.d_speed)
        print ('self.current_angle()', self.current_angle())
        print (' self.current_speed()', self.current_speed())
        if self.is_ready_angle(self.d_angle) and self.is_ready_speed(self.d_speed) == True:
            return True
        else:
            return False
        #returns true if the ShooterWheel is ready to shoot 


    def update(self):
        ''' Displays values on SmartDashboard if changed, sets angle and speed if not ready''' 
        if self.pre_angle != self.current_angle():
            wpilib.SmartDashboard.PutNumber('current_angle', self.current_angle())
        if self.pre_d_angle != self.d_angle:
            wpilib.SmartDashboard.PutNumber('desired_angle', self.d_angle)
        if self.pre_is_ready_angle != self.is_ready_angle(self.d_angle):
            wpilib.SmartDashboard.PutBoolean('is_ready_angle', self.is_ready_angle(self.d_angle))

        if self.pre_speed != self.current_speed():
            wpilib.SmartDashboard.PutNumber('current_speed', self.current_speed())
        if self.pre_d_speed != self.d_speed:
            wpilib.SmartDashboard.PutNumber('desired_speed', self.d_speed)
        if self.pre_is_ready_speed != self.is_ready_speed(self.d_speed):
            wpilib.SmartDashboard.PutBoolean('is_ready_speed', self.is_ready_speed(self.d_speed))
        #prints to SmartDashboard when the (6) values change        
       
        if self.pre_d_angle != self.d_angle:
            self.angle_jag.Set(self.d_angle)
        
        if self.is_ready_speed(self.d_speed) == True:
            self.shooter_jag.Set(0)
        
        else:
            self.shooter_jag.Set(1)
        #coast if the angle/speed is ready, full power if not.    
            
        self.pre_angle = self.current_angle()
        self.pre_speed = self.current_speed()
        self.pre_d_angle = self.d_angle
        self.pre_d_speed = self.d_speed
        self.pre_is_ready_angle = self.is_ready_angle(self.d_angle)
        self.pre_is_ready_speed = self.is_ready_speed(self.d_speed)
            
        
            
            
            
            
            
