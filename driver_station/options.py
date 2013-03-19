
import datetime
import os
import optparse

import target_detector.options

def _get_logdir_path():
    ''' Each time the application starts, we store logs in a different 
        directory that has a timestamp in its name
    
        do not call this function, use log_dir instead
    '''
    now = datetime.datetime.now().strftime('%Y-%m-%d %H%M-%S')
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs', now))


def configure_options():
    
    # TODO: integrate settings with options

    parser = optparse.OptionParser()
    
    parser.add_option('--robot-ip', dest='robot_ip', default=None,
                      help='Specified the IP address of the robot')
    
    parser.add_option('--logdir', dest='log_dir', default=_get_logdir_path(),
                      help='Directory to store logging information into')
    
    parser.add_option('--competition', dest='competition', default=False, action='store_true',
                      help='Set the dashboard to be in competition mode')
	
    target_detector.options.configure_options(parser)
    
    return parser
