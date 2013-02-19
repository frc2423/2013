
try:
    import wpilib
except ImportError:
    import fake_wpilib as wpilib


from .auto_jaguar import SpeedJaguar
from threading import Condition
from threading import Thread
    
class BangBangJaguar(SpeedJaguar):
    '''
        Implements a wrapper around a CANJaguar for automated control for 
        a bang bang motor controller
    '''
    #arbitrary large number not to conflict with 
    BANG_BANG = 99
    AUTO = BANG_BANG

    def __init__(self, motor, threshold):
        '''
            Constructor
            
            :param motor:     An EzCANJaguar instance, with all CAN/PID 
                              parameters set appropriately
            :param threshold: Amount position may vary to be considered correct
            
        '''
        super().__init__(motor, threshold)
        self.condition = Condition()
        self.set_value = 0
        self.bang_bang_thread = None
        self.run_bang_bang = None   
    
    #
    # Inquiries
    #
    
    def is_ready(self):
        '''
            Return True if the motor is in desired position/speed, False otherwise
            
            Note that in manual mode, this always returns True
        '''
        
        if self.mode == self.MANUAL:
            return True
        
        value = self.get_value()
        return abs(self.value - value) < self.threshold
    
    #
    # Update
    #
    
    def update(self):
        '''Sets the motor position/speed'''
        # BANG_BANG mode does this differently
        if self.mode == self.MANUAL:
            #if thread exists, pause it
            if self.bang_bang_thread != None:
                self.run_bang_bang = False
                
            self.motor.Set(self.value)
        
        else:
            self.set_value = self.value
            if self.bang_bang_thread == None:
                # if thread hasn't started yet, create it and start it
                self.bang_bang_thread = Thread(target = self._threaded_bang_bang)
                self.bang_bang_thread.setDaemon(True)
                self.bang_bang_thread.start()
           
            with self.condition:
                self.run_bang_bang = True
                self.condition.notify()
                    
        self.value = 0.0   
                     
        
    #
    # Thread on which to run
    #
    def _threaded_bang_bang(self):
        ''' 
            is to be run in separate thread launched when set into 
            BANG_BANG mode, only active while auto is in BANG_BANG mode
        '''
        self.keep_alive = True
        while self.keep_alive:
            
            with self.condition: 
                if not self.run_bang_bang:
                    self.condition.wait()
            
            speed = self.get_speed()
            sv = self.set_value
            if speed >= sv:
                self.motor.Set(-0.5)
            else:
                self.motor.Set(-1)
                
            wpilib.SmartDashboard.PutNumber('Speed', speed)
            wpilib.SmartDashboard.PutNumber('SetSpeed', sv)
