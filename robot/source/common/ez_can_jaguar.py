'''
    This class is designed to make some things with the CANJaguar that 
    are hard.. not quite so hard. 

'''

try:
    from wpilib import CANJaguar
except ImportError:
    from fake_wpilib import CANJaguar


class EzCANJaguar(CANJaguar):
    ''' 
        The CANJaguar requires you to do a lot of extra work when
        updating it. So here's how this works:
        
        - At initialization, call your various setup functions, and it
        stores your parameters somewhere
        - When you call ChangeControlMode, it remembers your 
        last parameters, sets them, and changes the mode appropriately
        
        Hints for PID stuff:
        - If it's not working for you, try negative values for your
        P, I, D
        
    '''

    def __init__(self, deviceNumber, controlMode=CANJaguar.kPercentVbus, cacheSetOps=True):
        CANJaguar.__init__(self, deviceNumber, controlMode)
        self.control_mode = controlMode
        self.cache_set_operations = cacheSetOps
        self.last_set = 0
    
    def ChangeControlMode(self, controlMode):
        
        if self.control_mode != controlMode:
            
            print('Change controlmode (old: %s, new: %s)' % (self.control_mode, controlMode))
            
            CANJaguar.ChangeControlMode( self, controlMode )
            self.control_mode = controlMode
            
            if controlMode == CANJaguar.kPercentVbus:
                CANJaguar.DisableControl(self)
                
            elif controlMode == CANJaguar.kCurrent:
                raise RuntimeError( "Not implemented" )
            
            elif controlMode == CANJaguar.kSpeed:
                CANJaguar.SetSpeedReference( self, self.speed_reference )
                CANJaguar.SetPID( self, self.pid[0]. self.pid[1], self.pid[2] )
                CANJaguar.EnableControl( self )
                
                print('-> Speed PID: %s %s %s' % self.pid)
                
            elif controlMode == CANJaguar.kPosition:
            
                CANJaguar.SetPositionReference( self, self.position_reference )
            
                if self.position_reference == CANJaguar.kPosRef_QuadEncoder:
                    CANJaguar.ConfigEncoderCodesPerRev(self, self.encoder_codes )
                elif self.position_reference == CANJaguar.kPosRef_Potentiometer:
                    CANJaguar.ConfigPotentiometerTurns(self, self.potentiometer_turns )
                    
                if hasattr(self, 'soft_position'):
                    CANJaguar.ConfigSoftPositionLimits( self, self.soft_position[0], self.soft_position[1] )
                
                CANJaguar.SetPID( self, self.pid[0], self.pid[1], self.pid[2] )
                
                if self.position_reference == CANJaguar.kPosRef_QuadEncoder:
                    CANJaguar.EnableControl( self, CANJaguar.GetPosition(self) )
                else:
                    CANJaguar.EnableControl( self )
                    
                print('-> Position PID: %s %s %s' % self.pid)
                
            elif controlMode == CANJaguar.kVoltage :
                raise RuntimeError( "Not implemented" )
            
    
    def ConfigEncoderCodesPerRev(self, codesPerRev):
        CANJaguar.ConfigEncoderCodesPerRev(self, codesPerRev)
        self.encoder_codes = codesPerRev
        
    def ConfigPotentiometerTurns(self, turns):
        CANJaguar.ConfigPotentiometerTurns( self, turns )
        self.potentiometer_turns = turns
        
    def ConfigSoftPositionLimits(self, min, max):
        CANJaguar.ConfigSoftPositionLimits( self, min, max )
        self.soft_position = (min, max)
    
    def DisableControl(self):
        raise AttributeError( "EzCANJaguar does not allow use of this function" )
    
    def EnableControl(self, encoderValue):
        raise AttributeError( "EzCANJaguar does not allow use of this function" )
        
    def Get(self):
        if self.cache_set_operations:
            return self.last_set
        return CANJaguar.Get(self)
        
    def Set(self, value, syncGroup=0):
        self.last_set = value
        CANJaguar.Set(self, value, syncGroup)
        
    def SetPID(self, p, i, d):
        if self.control_mode != CANJaguar.kPercentVbus:
            CANJaguar.SetPID( self, p, i, d )
        self.pid = (p, i, d)
        
    def SetPositionReference(self, reference):
        CANJaguar.SetPositionReference( self, reference )
        self.position_reference = reference
        
    def SetSpeedReference(self, reference):
        CANJaguar.SetSpeedReference( self, reference )
        self.speed_reference = reference
        
    
        
    