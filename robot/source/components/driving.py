'''
    Author: Arshdeep
'''

class Driving(object):
    '''
        Wrapper around the RobotDrive class for driving
    '''

    def __init__ (self, drive):
        self.drive = drive
        self.speed = None
     
    def drive(self, speed, rotate):
        '''Set driving parameters'''
        self.speed = speed
        self.rotate = rotate
       
    def update(self):
        '''Actually communicates with the motors'''
        
        if self.speed is not None:
            self.drive.ArcadeDrive(self.speed, self.rotate)
            self.speed = None
        else:
            self.drive.ArcadeDrive(0,0)
            