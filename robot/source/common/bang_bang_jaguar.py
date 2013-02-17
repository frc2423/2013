from .auto_jaguar import _AutoJaguar
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
        super.__init__(self, motor, threshold)
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
        
        if self.active_mode == self.MANUAL:
            return True
        
        value = self.get_value()
        return value >= (self.value - self.threshold) and value <= (self.value + self.threshold)
    
    #
    # Update
    #
    
    def update(self):
        '''Sets the motor position/speed'''
        # BANG_BANG mode does this differently
        if self.mode == MANUAL:
            #if thread exists, pause it
            if self.bang_bang_thread != None:
                self.run_bang_bang = False
                
            self.motor.Set(self.value)       
            self.value = 0.0
        
        else:
            self.set_value = self.value
            if self.bang_bang_thread == None:
                # if thread hasn't started yet, create it and start it
                self.bang_bang_thread = Thread(target = _threaded_bang_bang)
                self.bang_bang_thread.start()
                self.bang_bang_thread.join()
           
            #wait for thread to hit the running loop    
            while not self.run_bang_bang:
                with condition:
                    condition.notify()
        
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
            with condition: 
                self.condition.wait()
                self.run_bang_bang = True
                while self.run_bang_bang:
                    
                    if self.get_speed() >= self.set_value:
                        self.motor.Set(0)
        
                    else:
                        self.motor.Set(1)
