try:
    import wpilib
except ImportError:
    import fake_wpilib as wpilib
    
shooter_motor = wpilib.CANJaguar(3)

class shooter(object):
    
    def __init__(self,shooter_motor,switch2,switch1,):
        '''Parameters are shooter_motor, switch2, and switch 1... MTBA'''