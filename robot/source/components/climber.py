
try:
    import wpilib
except ImportError:
    import fake_wpilib as wpilib

class Climber(object):
    '''
        The climber is a set of pneumatic pistons that will raise/lower 
        the robot. There are two valves that cause air to move the pistons.
        
        When a climb/lower instruction is received, we have to continue 
        doing that thing for N number of seconds to keep the pistons on, 
        otherwise they will not fully extend/retract/whatever.
    '''

    
    CLIMB = 1
    LOWER = 2
    
    ACTION_PERIOD = 0.5
    
    def __init__(self, valve1, valve2):
        
        # values to move the pistons
        self.valve1 = valve1
        self.valve2 = valve2
        
        self.action_timer = wpilib.Timer()
        self.action_timer.Start()
        
        self.next_state = None
        self.current_state = None
    
    def climb(self):
        '''Call this to cause the robot to climb'''
        self.next_state = self.CLIMB
    
    def lower(self):
        '''Call this to lower the robot down to the ground'''
        self.next_state = self.LOWER
    
    def update(self):
        '''Actually perform the action'''
        
        # only transition when 
        if self.next_state is not None and self.next_state != self.current_state:
            self.current_state = self.next_state
            self.next_state = None
            self.action_timer.Reset()
        
        # idle state
        if self.current_state is None:
            self.valve1.Set(False)
            self.valve2.Set(False)
        else:
        
            if self.current_state == self.CLIMB:
                self.valve1.Set(False)
                self.valve2.Set(True)
            else:
                self.valve1.Set(True)
                self.valve2.Set(False)
            
            # do the action for a minimum period, then idle
            if self.action_timer.HasPeriodPassed(self.ACTION_PERIOD):
                self.current_state = None
