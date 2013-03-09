
# import this first
from common import logutil, settings

# ok, import stuff so we can get their versions
import pygtk
pygtk.require('2.0')
import gtk

import cv2
import numpy as np



if __name__ == '__main__':

    # initialize logging before importing anything that uses logging!
    ql = logutil.configure_logging()
    
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info('Starting Kwarqs Dashboard')

    # show versions
    logger.info('-> GTK %s.%s.%s' % gtk.gtk_version)
    logger.info('-> NumPy %s' % np.__version__)
    logger.info('-> OpenCV %s' % cv2.__version__)

    # initialize UI
    import ui

    # get options

    # determine what we're actually doing here
    
    
    # gtk main
    
    logger.info('Shutting down Kwarqs Dashboard')
    
    # shutdown anything needed here, like the logger
    ql.stop()
