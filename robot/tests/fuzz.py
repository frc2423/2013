'''
    The purpose of this 'test' is not exactly to 'do' anything, but
    rather it mashes the buttons and switches in various completely
    random ways to try and find any possible control situations and 
    such that would probably never *normally* come up, but.. well, 
    given a bit of bad luck, could totally happen. 
    
    Keep in mind that the results will totally different every time
    you run this, so if you find an error, fix it -- but don't expect
    that you'll be able to duplicate it with this test.
'''

import random
import _wpilib


# directory of robot.py, relative to this file
robot_path = '../source'

class Test(object):

    def __init__(self, robot_module, myrobot):
        self.robot_module = robot_module
        self.myrobot = myrobot
        
        self.dsc = self.robot_module.wpilib.DriverStation
        self.dsec = self.robot_module.wpilib.DriverStationEnhancedIO
        
        self.ds = self.robot_module.wpilib.DriverStation.GetInstance()
        self.eio = self.ds.GetEnhancedIO()
        
        self.digital_eio = [0]*16
        
        # sticks[stick_num][ axes, buttons ]
        self.sticks = []
        for i in range(0, self.dsc.kJoystickPorts):
            axes = [ 0.0 ] * self.dsc.kJoystickAxes
            buttons = [ 0.0 ] * 16
            self.sticks.append( (axes, buttons) )
            
        self.digital_inputs = [0]*16
        self.analog_channels = [0]*8
        
    def _fuzz_bool(self, tm, i, dst, tms):
                        
        if random.randrange(0,2,1) == 0:
            dst[i] = False
        else:
            dst[i] = True
            
        tms[i] = tm + random.random()
        
        
    def IsOperatorControl(self, tm):
    
        # fuzz the eio switches    
        for i, d_tm in enumerate(self.digital_eio):
        
            # inputs only
            if self.eio.digital_config[i] not in self.dsec._kInputTypes:
                continue
                
            # activate at random times
            if tm > d_tm:
                self._fuzz_bool(tm, i, self.eio.digital, self.digital_eio)

                
        # fuzz the joysticks
        for i,stick in enumerate(self.sticks):
            
            # axes 
            for j, a_tm in enumerate(stick[0]):
                if tm > a_tm:
                    self.ds.sticks[i][j] = random.uniform(-1,1)
                    stick[0][j] = tm + random.random()
            
            # buttons
            for j, b_tm in enumerate(stick[1]):
                if tm > b_tm:
                    self._fuzz_bool(tm, j, self.ds.stick_buttons[i], stick[1])
    
        # fuzz digital inputs
        for i, d_tm in enumerate(self.digital_inputs):
            di = self.robot_module.wpilib.DigitalModule._io[i]
            if isinstance(di, self.robot_module.wpilib.DigitalInput):
                if tm > d_tm:
                    if random.randrange(0,2,1) == 0:
                        di.value = False
                    else:
                        di.value = True
                    self.digital_inputs[i] = tm + random.random()
                    
        # fuzz analog channels
        for i, a_tm in enumerate(self.analog_channels):
            ac = self.robot_module.wpilib.AnalogModule._channels[i]
            if isinstance(ac, self.robot_module.wpilib.AnalogChannel):
                if tm > a_tm:
                    ac.voltage = random.uniform(0.0, 5.0)
                    self.analog_channels[i] = tm + random.random()
    
        # run a full match
        return tm < 105.0
        


def run_tests( robot_module, myrobot ):

    test = Test( robot_module, myrobot )
    
    _wpilib.internal.on_IsOperatorControl = test.IsOperatorControl
    _wpilib.internal.enabled = True
    
    myrobot.OperatorControl()


