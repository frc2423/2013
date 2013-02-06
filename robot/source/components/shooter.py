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
        self.c_speed = sendorA.GetSpeed()
        self.c_angle = sensorS.GetPosition() 
        
     
     def SetAngle(self):
        #sets the angle if it is not ready
        shooter_jag()     
    
    def SetSpeed(self):
        #Sets the speed if it is not ready
    
        
    def IsReadyAngle(self, d_angle):
        #returns true if desired angle and current angle are equal. 
        if c_angle > (d_angle - angle_threshhold) or (c_angle < d_angle + 1):
            return true
            
        else:
            shooter_jag.SetAngle
        
    def IsReadySpeed(self):
        #returns true if desired speed and current speed are equal.
        if c_speed > (d_speed - speed_threshhold) or (c_speed < d_speed + 1):
            return true
            
        else:
            shooter_jag.SetSpeed   
        
        
    
    def update(self):
        if self.updated == True:
            shooter_jag.shoot(self.angle, self.speed)
        else:
            self.updated = False
            
            