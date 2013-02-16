
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
    BANG_BANG = 99
    AUTO = None
    
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
        return value >= (self.value - self.threshold) and value <= (self.value + self.threshold)
        
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
            # BANG_BANG runs in manual mode
            if self.mode == self.BANG_BANG:
                self.mode = self.MANUAL
            # Set the control mode for the Jaguar appropriately
            self.motor.ChangeControlMode(self.mode)        
        
        # BANG_BANG mode does this diffrently
        if self.AUTO != BANG_BANG:
            # Both modes use the same function... 
            self.motor.Set(self.value)
            
            if self.motor.control_mode == self.MANUAL:            
                self.value = 0.0
        
        else:
            self.set_value = self.value


class PositionJaguar(_AutoJaguar):
    '''
        Implementation of a PID-controlled Jaguar for position
    '''
    
    AUTO = CANJaguar.kPosition
    
    def __init__(self, motor, threshold):
        '''See constructor for AutoJaguar'''
        self.get_value = self.motor.GetPosition
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
        Implementation of a PID-controlled or BANG BANG controlled Jaguar for 
        speed
    '''
    
    from threading import Lock
    from threading import Thread
    
    AUTO = CANJaguar.kSpeed
    ''' arbitrary large number as not to conflict with CANJaguars enums '''

    
    
    def __init__(self, motor, threshold):
        '''See constructor for AutoJaguar'''
        self.get_value = self.motor.GetSpeed
        _AutoJaguar.__init__(self, motor, threshold)
        self.bang_bang_thread = None
        self.condition = Condition()
        self.waiting = False
        self.set_value = 0
        
    def get_speed(self):
        '''Returns current speed as calculated by the speed reference'''
        return self.motor.GetSpeed()
    
    def set_speed(self, speed):
        '''Tell the motor to go to a specific speed'''
        self.mode = self.AUTO
        self.value = speed
        
    def set_auto_mode(self, mode): 
        '''sets auto mode to bang bang or PID'''
        if mode == self.BANG_BANG:
            self.AUTO = self.BANG_BANG
            # if thread hasn't started yet, create it and start it
            if self.bang_bang_thread == None:
                self.bang_bang_thread = Thread(target = _threaded_bang_bang)
                self.bang_bang_thread.start()
                self.bang_bang_thread.join()
                self.waiting = True
                
            while self.waiting:
                with condition:
                    condition.notify()
            
        else:
            self.AUTO = CANJaguar.kSpeed
            self.waiting = True
            
    def _threaded_bang_bang(self):
        ''' 
            is to be run in separate thread launched when set into 
            BANG_BANG mode, only active while auto is in BANG_BANG mode
        '''
        self.keep_alive = True
        #set mode to manual,set speed goals
        self.update()
        while self.keep_alive:
            with condition: 
                self.condition.wait()
                self.waiting = False
                while self.AUTO == self.BANG_BANG:
                    
                    if self.get_speed() >= self.set_value:
                        self.motor.Set(0)
        
                    else:
                        self.motor.Set(1)
