
import datetime
import logging
import logging.handlers
import os
import Queue

from loghandler_33 import QueueHandler, QueueListener

# TODO: Make these configurable
log_datefmt = "%H:%M:%S"
log_format = "%(asctime)s:%(msecs)03d %(levelname)-8s: %(name)-20s: %(message)s"
log_level = logging.DEBUG

def _get_logdir_path():
    ''' Each time the application starts, we store logs in a different 
        directory that has a timestamp in its name
    
        do not call this function, use log_dir instead
    '''
    now = datetime.datetime.now().strftime('%Y-%m-%d %H%M-%S')
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', now))

log_dir = _get_logdir_path()


def configure_logging():
    '''
        Configures the logger for the program. All logging will go over to
        a separate thread, which will then write the log to disk. This way 
        we can avoid blocking any of our processing threads.
    
        Do not import anything that requires the logger until we have setup 
        the logger.
        
        This returns a queue listener object. You should call stop() on it
        before exiting the program, or queued messages may be lost. 
    '''
        
    # get the root logger
    root = logging.getLogger("")
        
    # console logging
    logging.basicConfig(format=log_format, level=log_level, datefmt=log_datefmt)
           
    # log to a file
    log_file = os.path.join(log_dir, 'log')
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_exists = os.path.exists(log_file)
    
    file_logger = logging.handlers.RotatingFileHandler(log_file, mode='a', backupCount=10)
    
    if log_exists:
        file_logger.doRollover()
        
    file_logger.setFormatter(logging.Formatter(log_format, log_datefmt))
    
    # initialize the queues
    # -> the QueueListener starts a new thread
    q = Queue.Queue(-1)    
    ql = QueueListener(q, file_logger)
    
    qh = QueueHandler(q)
    root.addHandler(qh)
    
    ql.start()
    
    return ql
    
# function to store an image
#   - makes a copy of the image, stores it using another thread
