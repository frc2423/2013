from components import shooter_wheel
from components import feeder

class Shooter():

    def __init__(self, d_angle, d_speed):
        
        self.Updated = None
        self.d_angle = d_angle
        self.d_speed = d_speed
    def shoot_when_ready(self):
            
            if shooter_wheel.ShooterWheel.is_ready_angle(self, self.d_angle) == True and shooter_wheel.ShooterWheel.is_ready_speed() == True:
            
                self.Updated = True
                
            elif shooter_wheel.ShooterWheel.is_ready_angle(self, self.d_angle) == False and shooter_wheel.ShooterWheel.is_ready_speed() == True:
                
                self.updated = 3
                
            elif shooter_wheel.ShooterWheel.is_ready_angle(self, self.d_angle) == True and shooter_wheel.ShooterWheel.is_ready_speed() == False:
                
                self.updated = 4
    def continous_shoot(self):
    
        while feeder.Feeder.get_frisbee_count() > 0:
        
            if shooter_wheel.ShooterWheel.is_ready_angle() == True and shooter_wheel.ShooterWheel.is_ready_speed() == True:
            
                self.Updated = True
                
            elif shooter_wheel.ShooterWheel.is_ready_angle(self, self.d_angle) == False and shooter_wheel.ShooterWheel.is_ready_speed() == True:
                
                self.updated = 3
                
            elif shooter_wheel.ShooterWheel.is_ready_angle(self, self.d_angle) == True and shooter_wheel.ShooterWheel.is_ready_speed() == False:
                
                self.updated = 4
            
    def shoot_now(self):
    
        self.updated = True
        
    def set_angle(self):
        
        self.updated = 1 
        
    def set_speed(self):
        
        self.updated = 2
        
    def update(self):
        
        if self.updated == True:
        
            feeder.Feeder.feed()
            self.Updated = None
            
        if self.updated == 1:
            
            shooter_wheel.ShooterWheel.set_angle(self, self.d_angle)
            
        if self.updated == 2:
            
            shooter_wheel.ShooterWheel.set_angle(self, self.d_speed)
            
        if self.updated == 3:
            
            self.set_angle()
        
        if self.updated == 4:
            
            self.set_speed()