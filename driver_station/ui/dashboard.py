
import gtk

import util
from widgets import cv_widget

import logging
logger = logging.getLogger(__name__)


class Dashboard(object):
    '''
        This holds the main UI for the Kwarqs dashboard
    
        TODO: This is ugly, add pretty skins and stuff
    '''
    
    ui_filename = 'dashboard.ui'
    ui_widgets = [
        'window',
        
        'camera_image',
    ]
    ui_signals = [
        'on_window_destroy'
    ]
    
    def __init__(self):
        util.initialize_from_builder(self)
        
        self.camera_image = util.replace_widget(self.camera_image, cv_widget.CvWidget())
        
        # how does this work then?
        # -> create widgets
        # -> connect them to pynetworktables stuff somehow
        # -> show widgets?
        
        # -> is there a way to automatically do this with the gtk builder file perhaps?
        # --- sorta like initialize_from_builder on steroids? neat. 
        
        # -> start up the opencv thread? or does that happen in main
        # --- probably in main, it should talk to this, not the other
        #     way around. keep logic out of here if possible. 
        
        # first step needed: display the cv image on a pixbuf without too much
        # lag
        
        # also, how do we need to format the targeting information? Who keeps track 
        # of that? 
        
        # sdwidgets directory attaches widgets to a sd type? 
        
        # can we even get useful information from sd?
        # -> probably not, need better wrapper functions in SIP
        
        self.window.show_all()
        
        
    def on_window_destroy(self, widget):
        gtk.main_quit()