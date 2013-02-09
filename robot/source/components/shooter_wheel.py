try:
    import wpilib
except ImportError: 
    import fake_wpilib as wpilib
    

class ShooterWheel(object):
    
    
    def __init__(self, angle_jag, shooter_jag, angle_threshold, speed_threshold):
        self.updated = False
        self.shooter_jag = shooter_jag
        self.angle_jag = angle_jag
        self.angle_threshold = angle_threshold
        self.speed_threshold = speed_threshold
        
   def  current_speed(self):
        return shooter_jag.GetSpeed()
        
    def current_angle(self):
        return angle_jag.GetPosition() 
     
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
        self.d_speed = 0
        self.d_angle = 0
        
    def is_ready_angle(self, d_angle): 
        if self.current_angle() > (d_angle - self.angle_threshold) or (self.current_angle() < d_angle + self.angle_threshold):
            return True
            
        else:
            return False
        
   
    def is_ready_speed(self, d_speed):
        #returns true if desired speed and current speed are equal.
        if self.current_speed() > (self.d_speed - self.speed_threshold) or self.current_speed() < (self.d_speed + self.speed_threshold):
            return True
            
        else:
            return False
        
    def is_ready(self):
        if self.is_ready_angle(self.d_angle) and self.is_ready_speed(self.d_speed):
            return True
        else:
            return False
        
    
    def update(self):
        if self.d_speed <= self.current_speed():
            self.shooter_jag.set(0)
        else:
            self.shooter_jag.set(1)
       
        if self.d_angle <= self.current_angle():
            self.angle_jag.set(d_angle)
        
        else:
            self.angle_jag.set(1)
            
            self.updated = False    
            
            
            
            
            
            
