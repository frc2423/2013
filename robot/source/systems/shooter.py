from components import shooter_wheel
from components import feeder

class Shooter():

    def __init__(self,):
        
        self.Updated = None
        self.d_angle = shooter_wheel.ShooterWheel.d_angle
        self.d_speed = shooter_wheel.ShooterWheel.d_speed
    def shoot_when_ready(self):
            
            if shooter_wheel.ShooterWheel.is_ready_angle(self, self.d_angle) == True and shooter_wheel.ShooterWheel.is_ready_speed() == True:
            
                self.Updated = True
                
    def continous_shoot(self):
    
        while feeder.Feeder.get_frisbee_count() > 0:
        
            if shooter_wheel.ShooterWheel.is_ready_angle(self, self.d_angle)IsReadyAngle() == True and shooter_wheel.ShooterWheel.IsReadySpeed() == True:
            
                self.Updated = True
            
    def shoot_now(self):
    
        self.Updated = True
            		
    def update():
        
        if self.updated == True
        
            feeder.Feed()
            self.Updated = None
     