'''
    Implements an operator control mode management program. Example usage:
    
        from manual import OperatorControlManager
        
        components = {'drive': drive, 
                      'component1': component1, ... }
        operator_control = OperatorControlManager(components)
        
        class MyRobot(wpilib.SimpleRobot):
        
            ... 
            
            def OperatorControl(self):
                operatorcontrol.run(self, control_loop_wait_time)
                
            def update(self):
            
                ... 
    
    Note that the robot instance passed to OperatorControlManager.run() must
    have an update function. 
'''

from glob import glob
import imp
import inspect
import os
import sys

try:
    import wpilib
except ImportError:
    import fake_wpilib as wpilib


class OperatorControlManager(object):
    '''
        The operator  manager loads all operator  mode modules and allows
        the user to select one of them via the SmartDashboard. 
        
        See template.txt for a sample operator  mode module
    '''
    
    def __init__(self, components):
        
        self.ds = wpilib.DriverStation.GetInstance()
        self.modes = {}
        self.active_mode = None
        
        print( "OperatorControlManager::__init__() Begins" )
        
        # load all modules in the current directory
        modules_path = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(modules_path)
        modules = glob(os.path.join(modules_path, '*.py' ))
        
        for module_filename in modules:
            
            module_name = os.path.basename(module_filename[:-3])
            
            if module_name in  ['__init__', 'manager']:
                continue
        
            try:
                module = imp.load_source(module_name, module_filename)
            except:
                if not self.ds.IsFMSAttached():
                    raise
            
            #
            # Find operator control mode classes in the modules that are present
            # -> note that we actually create the instance of the objects here,
            #    so that way we find out about any errors *before* we get out 
            #    on the field.. 
            
            for name, obj in inspect.getmembers(module, inspect.isclass):

                if hasattr(obj, 'MODE_NAME') :
                    try:
                        instance = obj(components)
                    except:
                        
                        if not self.ds.IsFMSAttached():
                            raise
                        else:
                            continue
                    
                    if instance.MODE_NAME in self.modes:
                        if not self.ds.IsFMSAttached():
                            raise RuntimeError( "Duplicate name %s in %s" % (instance.MODE_NAME, module_filename) )
                        
                        print( "ERROR: Duplicate name %s specified by object type %s in module %s" % (instance.MODE_NAME, name, module_filename))
                        self.modes[name + '_' + module_filename] = instance
                    else:
                        self.modes[instance.MODE_NAME] = instance
        
        # now that we have a bunch of valid operator  mode objects, let 
        # the user select one using the SmartDashboard.
        
        # SmartDashboard interface
        sd = wpilib.SmartDashboard
        self.chooser = wpilib.SendableChooser()
        sd.PutData('Operator Control Mode', self.chooser) 
        
        print("Loaded operator control modes:")
        for k,v in self.modes.items():
            
            if hasattr(v, 'DEFAULT') and v.DEFAULT == True:
                print(" -> %s [Default]" % k)
                self.chooser.AddDefault(k, v)
            else:
                print( " -> %s" % k )
                self.chooser.AddObject(k, v)
        
        print( "OperatorControlManager::__init__() Done" )
    
            
    def run(self, robot):    
        '''
            This function does everything required to implement operator control
            mode behavior. 
            
            :param robot: a SimpleRobot derived class, and is expected to 
                          have a function called 'update', which will do 
                          updates on all motors and components.
                          
        '''
        
        print("OperatorControlManagerr::operator ()")
             
        try:
            self.on_operator_control_enable()
        except:
            if not self.ds.IsFMSAttached():
                raise
        
        # set the watch dog
        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExpiration(0.25)
        
        # put this in a consistent state when starting the robot
        self.my_climber.lower()
        compressor.Start()
        
        #
        # operator  control loop
        #
        

        while robot.IsOperatorControl () and robot.IsEnabled():
            # measure loop time
            start = wpilib.Timer.GetPPCTimestamp()
            try:            
                self.set()
            except:
                if not self.ds.IsFMSAttached():
                    raise
            
            robot.update()
            
            # how long does it take us to run the loop?
            # -> we're using a lot of globals, what happens when we change it?
            wpilib.SmartDashboard.PutNumber('Loop time', wpilib.Timer.GetPPCTimestamp() - start)
            
            wpilib.Wait(control_loop_wait_time)
            dog.Feed()
            
        #
        # Done with operator mode, finish up
        #
        compressor.Stop()     
        try:
            self.on_operator_control_disable()
        except:
            if not self.ds.IsFMSAttached():
                raise
    
    #
    #   Internal methods used to implement operator  mode switching. Most
    #   users of this class will not want to use these functions, use the
    #   run() function instead. 
    #
    
    def on_operator_control_enable(self):
        '''Select the active operator control mode here, and enable it'''
        self.active_mode = self.chooser.GetSelected()
        if self.active_mode is not None:
            print("OperatorControlManagerr: Enabling %s" % self.active_mode.MODE_NAME)
            self.active_mode.on_enable()
 
    def on_operator_control_disable(self):
        '''Disable the active operator control'''
        if self.active_mode is not None:
            print("OperatorControlManagerr: Disabling %s" % self.active_mode.MODE_NAME)
            self.active_mode.on_disable()
            
        self.active_mode = None
        
    def set(self): 
        '''Run the code for the current operator control mode'''
        if self.active_mode is not None:
            self.active_mode.set()
   
    #update done up top to all robot systems
    #def update(self):
    #    '''Run the code for the current operator control mode'''
    #    if self.active_mode is not None:
    #        self.active_mode.update()

