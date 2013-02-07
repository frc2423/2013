try:
    import wpilib
except ImportError: 
    import fake_wpilib as wpilib
    

class ShooterWheel(object):
    
    
    def __init__(self, shooter_jag, angle_threshold, speed_threshold):
        self.updated = False
        self.shooter_jag = shooter_jag
        self.c_speed = shooter_jag.GetSpeed()
        self.c_angle = shooter_jag.GetPosition() 
     
    def set_angle(self, d_angle):
        self.updated = True
        self.d_angle = d_angle
        #sets the angle if it is not ready
        self.shooter_jag.Set(self.d_angle)
    
    
    def set_speed(self, d_speed):
        self.updated = True
        self.d_speed = d_speed
        #Sets the speed if it is not ready
        self.shooter_jag.Set(self.d_speed)
        
        
    def stop(self):
        self.updated = True
        self.shooter_jag.Set(0)
    
        
    def is_ready_angle(self, d_angle): 
        if self.c_angle > (d_angle - self.angle_threshold) or (self.c_angle < d_angle + self.angle_threshold):
            return True
            
        else:
            return False
        
   
    def is_ready_speed(self):
        #returns true if desired speed and current speed are equal.
        if self.c_speed > (self.d_speed - self.speed_threshold) or self.c_speed < (self.d_speed + self.speed_threshold):
            return True
            
        else:
            return False
        
    
    def update(self):
        if self.updated == True:
            self.SetAngle(self.d_angle)
            self.SetSpeed(self.d_speed)
            self.updated = False    