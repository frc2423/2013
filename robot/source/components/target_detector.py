
try:
    from wpilib import NetworkTable, ITableListener
except ImportError:
    from fake_wpilib import NetworkTable, ITableListener

import threading


    
class TargetDetector(object):
#class TargetDetector(ITableListener):
    '''
        Client that runs on the cRio to receive targeting information from the
        image processing software on the driver station
        
        Data received from image processing:
            - target horizontal angle
            - target distance
    '''
    
    def __init__(self, table_name='SmartDashboard'):
        # ITableListener.__init__(self)
        
        self.lock = threading.Lock()
        
        self.hangle = None
        self.vangle = None
        self.distance = None
        
        self.table = NetworkTable.GetTable(table_name)
        
        self.table.PutBoolean('Target Found', False)
        self.table.PutNumber('Target HAngle', 0)
        self.table.PutNumber('Target VAngle', 0)
        self.table.PutNumber('Target Distance', 0)
        
        # table.AddTableListener('targeting', self, False)
        
    def get_data(self):
        '''Returns a tuple of horizontal angle, vertical angle, distance. Check to see
           if any of them are None before using them
           
           TODO: I don't like this. What if the remote end crashes? Then we're working
           off of invalid data. 
        '''
        
        # TODO: needs to be atomic
        if self.table.GetBoolean('Target Found') != True:
            return None, None, None
        
        return (self.table.GetNumber('Target HAngle'),
               self.table.GetNumber('Target VAngle'),
               self.table.GetNumber('Target Distance'))
        
        #with self.lock:
        #    return self.hangle, self.vangle, self.distance
        
    def ValueChanged(self, table, key, value, isNew):
        '''NetworkTables interface that notifies us that a value changed'''
        
        # TODO: Change this, it's terrible
        v = [float(v) for v in table.GetString(key).split(' ')]
        
        with self.lock:
            self.hangle = v[0]
            self.vangle = v[1]
            self.distance = v[2]

    # No update function required
