try:
    import wpilib
except ImportError: 
    import fake_wpilib as wpilib
    

class ShooterWheel(object):
    
    def __init__(self, motorA, motorS, sensorA, sensorS, shooter_jag, d_speed, d_angle, angle_threshhold, speed_threshhold):
        self.updated = False
        self.shooter_jag = shooter_jag
        self.sensorA = sensorA
        self.sensorS = sensorS
        self.c_speed = sensorA.GetSpeed()
        self.c_angle = sensorS.GetPosition() 
        
     
    def SetAngle(self, d_angle):
        self.updated = True
        self.d_angle = d_angle
        #sets the angle if it is not ready
        self.shooter_jag.Set(self.d_angle)
    
    def SetSpeed(self, d_speed):
        self.updated = True
        self.d_speed
        #Sets the speed if it is not ready
        self.shooter_jag.Set(self.d_speed)
        
    def stop(self):
        self.updated = True
        self.shooter_jag.Set(0)
    
        
    def IsReadyAngle(self, d_angle): 
        if self.c_angle > (d_angle - self.angle_threshhold) or (self.c_angle < d_angle + self.angle_threshhold):
            return True
            
        else:
            return False
        
   
    def IsReadySpeed(self):
        #returns true if desired speed and current speed are equal.
        if self.c_speed > (self.d_speed - self.speed_threshhold) or self.c_speed < (self.d_speed + self.speed_threshhold):
            return True
            
        else:
            return False
        
    
    def update(self):
        if self.updated == True:
            self.SetAngle(self.d_angle)
            self.SetSpeed(self.d_speed)
            self.updated = False
            
            