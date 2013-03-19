
# directory that robot.py is located, relative to this file
robot_path = '../source'

import _wpilib

class Test(object):

    def __init__(self, robot_module, myrobot):
        self.robot_module = robot_module
        self.myrobot = myrobot
        data = _wpilib.SmartDashboard._table.data
        
        # if there are choosers, make sure to run them through their choices
        # so create 
        self.op_chooser = None
        self.auto_chooser = None
        
        if hasattr(myrobot, "operator_control_mode"):
            self.op_chooser = myrobot.operator_control_mode.control_mode_chooser
            self.op_iterator = iter(self.op_chooser.choices)

        if hasattr(myrobot, "autonomous_mode"):
            self.auto_chooser = myrobot.autonomous_mode.chooser
            self.auto_iterator = iter(self.auto_chooser.choices)
    
        self.Reset()
        
    def Reset(self):
        self.loop_count = 0
        self.tm = None
        
    def IsAutonomous(self, tm):
        '''Run a full 15 seconds of autonomous mode, per mode, then exit'''
        if self.tm is None:
            self.tm = tm
        
        if self.auto_chooser is not None:   
            if tm % 15:
                try:
                    self.auto_chooser.selected = self.auto_iterator.__next__()
                    self.myrobot.autonomous_mode.on_autonomous_enable()
                except StopIteration:
                    return False 
            
        return tm - self.tm < 15.0
        
    def IsOperatorControl(self, tm):
        '''
            If there is a chooser iterate through it until we have gone through
            all the modes else continue operator control for 1000 control loops
        '''
        self.loop_count += 1
        if self.op_chooser is not None:
            if tm % 2:
                try:
                    self.op_chooser.selected = self.op_iterator.__next__()
                except StopIteration:
                    return False 
        
            return True
        else:
            return not self.loop_count == 1000


def run_tests( robot_module, myrobot ):
    
    test = Test( robot_module, myrobot )

    _wpilib.internal.print_components()
    
    _wpilib.internal.on_IsAutonomous = test.IsAutonomous
    _wpilib.internal.on_IsOperatorControl = test.IsOperatorControl
    
    
    _wpilib.internal.enabled = True
    
    test.Reset()
    myrobot.Autonomous()
    
    test.Reset()
    myrobot.OperatorControl()


