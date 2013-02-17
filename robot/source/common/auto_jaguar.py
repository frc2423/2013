
try:
    from wpilib import CANJaguar
except ImportError:
    from fake_wpilib import CANJaguar


class _AutoJaguar(object):
    '''
        Implements a wrapper around a CANJaguar for automated control, and
        provides PID-based and manual control.
        
        Don't use this class directly, use PositionJaguar or SpeedJaguar
        instead.        
    '''
    
    MANUAL = CANJaguar.kPercentVbus
    
    def __init__(self, motor, threshold):
        '''
            Constructor
            
            :param motor:     An EzCANJaguar instance, with all CAN/PID 
                              parameters set appropriately
            :param threshold: Amount position may vary to be considered correct
        '''
        self.motor = motor
        
        self.threshold = threshold
        self.mode = None
        self.value = 0.0
        
        self.motor.ChangeControlMode(self.MANUAL)
        self.motor.Set(0.0)
        
    #
    # Inquiries
    #
    
    def is_ready(self):
        '''
            Return True if the motor is in desired position/speed, False otherwise
            
            Note that in manual mode, this always returns True
        '''
        if self.motor.control_mode == self.MANUAL:
            return True
        
        value = self.get_value()
        return abs(self.value - value) <= self.threshold
        
    #
    # Actions
    #
        
    def set_manual_motor_value(self, value):
        '''Manually move the motor up and down'''        
        self.mode = self.MANUAL
        self.value = value
        
    #
    # Update
    #
    
    def update(self):
        '''Sets the motor position/speed'''
        
        if self.mode is not None:
            # Set the control mode for the Jaguar appropriately
            self.motor.ChangeControlMode(self.mode)
            self.mode = None
        
        # Both modes use the same function... 
        self.motor.Set(self.value)
        
        if self.motor.control_mode == self.MANUAL:            
            self.value = 0.0


class PositionJaguar(_AutoJaguar):
    '''
        Implementation of a PID-controlled Jaguar for position
    '''
    
    AUTO = CANJaguar.kPosition
    
    def __init__(self, motor, threshold):
        '''See constructor for AutoJaguar'''
        self.get_value = motor.GetPosition
        _AutoJaguar.__init__(self, motor, threshold)
        
    def get_position(self):
        '''Returns current position as calculated by the position reference'''
        return self.motor.GetPosition()
    
    def set_position(self, position):
        '''Tell the motor to go to a specific position'''
        self.mode = self.AUTO
        self.value = position
    
    
class SpeedJaguar(_AutoJaguar):
    '''
        Implementation of a PID-controlled Jaguar for speed
    '''
    
    AUTO = CANJaguar.kSpeed
    
    def __init__(self, motor, threshold):
        '''See constructor for AutoJaguar'''
        self.get_value = motor.GetSpeed
        _AutoJaguar.__init__(self, motor, threshold)
    
    def get_speed(self):
        '''Returns current speed as calculated by the speed reference'''
        return self.motor.GetSpeed()
    
    def set_speed(self, speed):
        '''Tell the motor to go to a specific speed'''
        self.mode = self.AUTO
        self.value = speed

