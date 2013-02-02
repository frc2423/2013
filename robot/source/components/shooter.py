try:
    import wpilib
except ImportError:
    import fake_wpilib as wpilib
    

class shooter(object):
    
    def __init__(self, motorA, motorS, sensorA, sensorS, shooter_jag, d_speed, d_angle):
        self.updated = False
        self.shooter_jag = shooter_jag
        self.sensorA = sensorA
        self.sensorS = sensorS
             
    def shoot(self, speed, angle):
        self.shooter_jag
        self.sensorA
        self.sensorS 
        self.speed = speed
        self.angle = angle
        if d_speed = speed and d_angle = angle:
            self.updated = True
        else:
             self.updated = False
        
    
    def update(self):
        if self.updated == True:
            shooter_jag.shoot(self.angle, self.speed)
        else:
            self.updated = False
            
            