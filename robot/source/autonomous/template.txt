'''
    Author: Who wrote this?
    Date:   When was it written?
    
    Description:
    
        Put a useful description of your autonomous mode here
'''

class MyAutonomousMode(object):

    # this name should be descriptive and unique. This will be shown to the user
    # on the SmartDashboard
    MODE_NAME = "NameOfMode"
    
    # Set this to True if this is the default autonomous mode, otherwise False
    DEFAULT = False


    def __init__(self, components):
        '''Constructor: store components locally here'''
        self.drive = components['drive']
        
        # and so on, for each component that you need... 
        
    def on_enable(self):
        '''
            This function is called when Autonomous mode is enabled. You should
            initialize things needed for your mode here
        '''
        
        pass
        
    def on_disable(self):
        '''
            This function is called when Autonomous mode is exiting. You should
            clean anything up here that needs to be cleaned up
        '''
        
        pass
        
    def update(self, time_elapsed):
        '''
            This function is called every 10ms or so. This is where you should
            make decisions about what needs to happen in your autonomous mode.
            You do not need to call the 'Update' functions of any components
            here, as they will be called for you automatically.
            
            time_elapsed is the number of seconds that autonomous mode has been
            active, in case your mode finds that useful. 
        '''
        
        pass
