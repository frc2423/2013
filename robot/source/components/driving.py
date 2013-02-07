try:
    import wpilib 
except ImportError:
    import fake_wpilib as wpilib 
    
    
class Driving(object):

    def __init__ (self, drive):
        self.updated = False
        self.drive = drive 
     
    def drive(self, rot, speed):
        self.updated =  True
        self.rot = rot
        self.speed = speed       
       
    def update(self):
        if self.updated == True:
            self.drive.ArcadeDrive(self.speed, self.rot)
            
        else:
            self.drive.ArcadeDrive(0,0)
            self.updated = False
        
            