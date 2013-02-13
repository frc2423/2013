try:
    import wpilib
except ImportError: 
    import fake_wpilib as wpilib
    

class ShooterWheel(object):
    
    
    def __init__(self, angle_jag, shooter_jag, angle_threshold, speed_threshold):
        self.updated = False
        self.angle_jag = angle_jag
        self.shooter_jag = shooter_jag
        self.angle_threshold = angle_threshold
        self.speed_threshold = speed_threshold
       
    def current_angle(self):
        return self.angle_jag.GetPosition()   
    
    def current_speed(self):
        return self.shooter_jag.GetSpeed()
     
    def set_angle(self, d_angle):
        self.updated = True
        self.d_angle = d_angle
        #sets the angle if it is not ready
    
    def set_speed(self, d_speed):
        self.updated = True
        self.d_speed = d_speed
        #Sets the speed if it is not ready
        
    def stop(self):
        self.updated = True
        self.d_angle = 0
        self.d_speed = 0
        
    def is_ready_angle(self, d_angle): 
        if self.current_angle() >= (self.d_angle - self.angle_threshold) and self.current_angle() <= (self.d_angle + self.angle_threshold):
            return True
            
        else:
            return False
        
   
    def is_ready_speed(self, d_speed):
        #returns true if desired speed and current speed are equal.
        if self.current_speed() >= (self.d_speed - self.speed_threshold) and self.current_speed() <= (self.d_speed + self.speed_threshold):
            return True
            
        else:
            return False
        
    def is_ready(self):
        print ('self.d_angle =', self.d_angle)
        print ('self.d_speed =', self.d_speed)
        print ('self.current_angle()', self.current_angle())
        print (' self.current_speed()', self.current_speed())
        if self.is_ready_angle(self.d_angle) and self.is_ready_speed(self.d_speed) == True:
            return True
        else:
            return False 


    def update(self):
        self.updated = True
        if self.pre_angle != self.current_angle():
            wpilib.SmartDashboard.PutNumber('current_angle', self.current_angle())
        if self.pre_d_angle != self.d_angle:
            wpilib.SmartDashboard.PutNumber('d_angle', self.d_angle)
        if self.pre_is_ready_angle != self.is_ready_angle(self.d_angle):
            wpilib.SmartDashboard.PutBoolean('is_ready_angle', self.is_ready_angle(self.d_angle))


        if self.pre_speed != self.current_speed():
            wpilib.SmartDashboard.PutNumber('current_speed', self.current_speed())
        if self.pre_d_speed != self.d_speed:
            wpilib.SmartDashboard.PutNumber('d_speed', self.d_speed)
        if self.pre_is_ready_speed != self.is_ready_speed(self.d_speed):
            wpilib.SmartDashboard.PutBoolean('is_ready_speed', self.is_ready_speed(self.d_speed)        
        
        
         if self.is_ready_angle == True():
            self.angle_jag.set(0)
        
        else:
            self.angle_jag.set(1)
       
        
        if self.is_ready_speed() == True:
            self.shooter_jag.set(0)
        
        else:
            self.shooter_jag.set(1)
            
            
            self.updated = False    
            self.pre_angle = self.current_angle()
            self.pre_speed = self.current_speed()
            self.pre_d_angle = self.d_angle
            self.pre_d_speed = self.d_speed
            self.pre_is_ready_angle = self.is_ready_angle(self.d_angle)
            self.pre_is_ready_speed = self.is_ready_speed(self.d_speed)
            
        
            
            
            
            
            
