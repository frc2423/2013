try:
    import wpilib
except ImportError: 
    import fake_wpilib as wpilib
    

class ShooterPlatform(object):
    ''' Handles shooter and angle components together'''
    
    LOWER_ANGLE_SPEED = 1.0
    
    def __init__(self, angle_jag, shooter_jag, climber):
        ''' 
            Initializes ShooterPlatform object
            
            Parameters:
                angle_jag -- an AutoJaguar configured for position control
                shooter_jag -- an AutoJaguar configured for speed control
        '''
        self.updated = False
        
        #jaguars
        self.angle_jag = angle_jag
        self.shooter_jag = shooter_jag
        
        self.climber = climber
        
        #desired states
        self.d_angle = 0
        self.d_speed = 0
        self.pre_d_angle = None
        self.pre_d_speed = None
        self.pre_adt = None 
        self.pre_sdt = None
        
        #current states
        self.pre_angle = None
        self.pre_speed = None

        #is ready
        self.pre_is_ready_angle = None
        self.pre_is_ready_speed = None
        
        #mode
        self.wheel_on = False
       
    def current_angle(self):
        ''' Gets the real angle '''
        return self.angle_jag.get_position()   
    
    def current_speed(self):
        ''' Gets the real speed'''
        return self.shooter_jag.get_speed()
    
    def at_zero(self):
        '''Returns True if the platform is in the forward position'''
        
        # use the limit switch in case the pot breaks
        return not self.angle_jag.motor.GetForwardLimitOK()
    
    def set_on(self):
        self.wheel_on =True
        
    def set_off(self):
        self.wheel_on = False
        
    def set_speed(self, speed):
        ''' sets speed based on the mode it is in '''
        if  self.wheel_on:
            self.set_speed_manual(speed)
        else:
            self.set_speed_manual(0)
         
    def set_angle_auto(self, d_angle):
        '''
            Presets the angle automatically to the desired angle stores the past 
            parameter with the instance. Must call Update() to actually set
            the motor to go to said value.
            
            param : d_angle - The desired angle
        '''
        if self.climber.position() == self.climber.LOWER:
            self.angle_jag.set_angle(d_angle)
            self.d_angle = d_angle

    
    def set_speed_auto(self, d_speed):
        '''
            Presets the angle automatically to the desired speed stores the past 
            parameter w/ the instance. Must call Update() to actually set
            the motor to go to said value.
            
            param : d_angle - The desired angle
        '''
        self.shooter_jag.set_speed(d_speed)
        self.d_speed = d_speed
        
    def set_angle_manual(self, d_angle):
        '''
            Presets the angle manually using %Vbus to the desired angle.
            Must call Update() to actually set
            the motor to go to said value.
            
            param : d_angle - The desired angle
        '''
        if d_angle > 0 or self.climber.position() == self.climber.LOWER:
            self.angle_jag.set_manual_motor_value(d_angle)
            self.d_angle = 0

    def set_speed_manual(self, d_speed):
        '''
            Presets the angle manually using %Vbus to the desired speed.
            Must call Update() to actually set
            the motor to go to said value.
            
            param : d_angle - The desired angle
        '''
        self.shooter_jag.set_manual_motor_value(d_speed)
        self.d_speed = 0
        
    def is_ready_angle(self):
        ''' checks if the angle is right''' 
        #returns true if current angle is within threshold.
        return self.angle_jag.is_ready()
   
    def is_ready_speed(self):
        ''' checks if the speed is right'''
        #returns true if current speed is within threshold.
        return self.shooter_jag.is_ready()
        
    def is_ready(self):
        ''' checks if the shooter_platform is ready to shoot'''
        #returns true if shooter_platform is ready to shoot
        return self.wheel_jag.is_ready() and self.angle_jag.is_ready()
            
    def _update_smart_dashboard(self):
        ''' 
            Displays values on SmartDashboard if changed
        ''' 
        
        #
        # Displays angle info
        #
        wpilib.SmartDashboard.PutNumber('Angle Raw', self.angle_jag.motor.GetPosition())
        ca = self.current_angle()
        if self.pre_angle != self.current_angle():
            wpilib.SmartDashboard.PutNumber('Angle', ca)
        
        if self.pre_d_angle != self.d_angle:
            wpilib.SmartDashboard.PutNumber('Angle Desired', self.d_angle)
            
        # tuning: difference between speed and desired speed
        adt = self.d_angle - ca
        if self.pre_adt != adt:
            wpilib.SmartDashboard.PutNumber('Angle DT', self.d_angle - ca)
            self.pre_adt = adt
        
        if self.pre_is_ready_angle != self.is_ready_angle():
            wpilib.SmartDashboard.PutBoolean('Angle Ready', self.is_ready_angle())

        #
        # Displays speed info
        #
        
        cs = self.current_speed()
        if self.pre_speed != self.current_speed():
            wpilib.SmartDashboard.PutNumber('WSpeed', cs)
            
        if self.pre_d_speed != self.d_speed:
            wpilib.SmartDashboard.PutNumber('WSpeed Desired', self.d_speed)
            
        # tuning: difference between speed and desired speed
        sdt = self.d_speed - cs
        if self.pre_sdt != sdt:
            wpilib.SmartDashboard.PutNumber('WSpeed DT', sdt)
            self.pre_sdt = sdt
            
        if self.pre_is_ready_speed != self.is_ready_speed():
            wpilib.SmartDashboard.PutBoolean('WSpeed Ready', self.is_ready_speed())
             

    def update(self):
        ''' 
            Updates speed and position of angle and  displays on the smartdashboard
        '''
        
        #
        #update smart dashboard
        #
        self._update_smart_dashboard()
        
        #
        #Update jags, the AutoJag class handles the hard stuff
        #
        self.angle_jag.update()
        self.shooter_jag.update()
        
        #
        #Set all pre variables, since we are done with the current ones
        #
        self.pre_angle = self.current_angle()
        self.pre_speed = self.current_speed()
        self.pre_d_angle = self.d_angle
        self.pre_d_speed = self.d_speed
        self.pre_is_ready_angle = self.is_ready_angle()
        self.pre_is_ready_speed = self.is_ready_speed()
            
        
            
            
            
            
            
