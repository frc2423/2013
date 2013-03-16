'''
    Author: Arshdeep
'''

class Driving(object):
    '''
        Wrapper around the RobotDrive class for driving1
    '''

    def __init__ (self, robot_drive):
        self.robot_drive = robot_drive
        self.speed = None
     
    def drive(self, speed, rotate, faster=False):
        '''Set driving parameters'''
        self.speed = speed
        self.rotate = rotate * 0.7
        self.faster = faster
       
    def update(self):
        '''Actually communicates with the motors'''
        
        if self.speed is not None:
            self.robot_drive.ArcadeDrive(self.speed, self.rotate, not self.faster)
            self.speed = None
        else:
            self.robot_drive.ArcadeDrive(0,0)