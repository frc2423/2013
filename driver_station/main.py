
import sys

from common import logutil, settings
from options import configure_options

# ok, import stuff so we can get their versions
import pygtk
pygtk.require('2.0')
import gtk

import cairo

import cv2
import numpy as np


def initialize_pynetworktables(ip):
    
    if ip is not None:
        
        from pynetworktables import NetworkTable
        
        NetworkTable.SetIPAddress(ip)
        NetworkTable.SetClientMode()
        NetworkTable.Initialize()
        
        return NetworkTable.GetTable(u'SmartDashboard')
    

if __name__ == '__main__':
    
    # get options first
    parser = configure_options()
    options, args = parser.parse_args()
    
    # initialize logging before importing anything that uses logging!
    ql = logutil.configure_logging(options.log_dir)
    
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info('Starting Kwarqs Dashboard')

    # show versions
    logger.info('-> Python %s' % sys.version.replace('\n', ' '))
    logger.info('-> GTK %s.%s.%s' % gtk.gtk_version)
    logger.info('-> Cairo %s' % cairo.version)
    logger.info('-> NumPy %s' % np.__version__)
    logger.info('-> OpenCV %s' % cv2.__version__)
    
    # configure and initialize things    
    table = initialize_pynetworktables(options.robot_ip)

    # initialize UI
    import ui.dashboard
    dashboard = ui.dashboard.Dashboard()

    import target_detector.processing

    
    # setup the image processing and start it
    try:
        processor = target_detector.processing.ImageProcessor(options,
                                                              dashboard.camera_widget)
    except RuntimeError:
        exit(1)
        
    processor.start()
    
    # gtk main
    dashboard.show_all()
    
    gtk.threads_init()
    gtk.main()
    
    
    logger.info('Shutting down Kwarqs Dashboard')
    
    # shutdown anything needed here, like the logger
    processor.stop()
    ql.stop()

