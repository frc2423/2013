
import gtk

import util
from widgets import targeter, camera_settings, robot_widget, image_button, toggle_button 

import logging
logger = logging.getLogger(__name__)


class Dashboard(object):
    '''
        This holds the main UI for the Kwarqs dashboard
    
        TODO: This is ugly, add pretty skins and stuff
        
        TODO: More modular, but using a UI file this way doesn't
        lend itself to that.. well, maybe if we pass the builder
        in to the module? Hm. 
    '''
    
    ui_filename = 'dashboard.ui'
    ui_widgets = [
        'window',
        
        'camera_widget',
        'robot_widget',
        
        'climbing_mode_button',
        'loading_mode_button',
        'manual_mode_button',
        'shooting_mode_button',
        
        'wheel_status',
        'ready_status',
        'horizontal_status',
        'vertical_status',
        
        'fire_button',
        'wheel_on_button',
        
        'autonomous_chooser',
        
    ]
    ui_signals = [
        'on_cancel_targeting_button_clicked',
        'on_window_destroy'
    ]
    
    def __init__(self, processor, table, competition):
        
        self.camera_settings = camera_settings.CameraSettings(processor)
        
        util.initialize_from_xml(self, [self.camera_settings])
        
        self.camera_widget = util.replace_widget(self.camera_widget, targeter.Targeter((640,480), table))

        self.robot_widget = util.replace_widget(self.robot_widget, robot_widget.RobotWidget(table))

        self.camera_settings.initialize()
       
        self.table = table
        
        self.window.set_title("Kwarqs Dashboard")
        self.window.connect('realize', self.on_realize)
       
        if competition:
            self.window.move(0,0)
            self.window.resize(1356, 525)
            
        # load the status buttons
        active_pixbuf = util.pixbuf_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
        inactive_pixbuf = util.pixbuf_from_stock(gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON)
        
        for name in ['wheel_status', 'ready_status', 'horizontal_status', 'vertical_status']:
            old_widget = getattr(self, name)
            text = old_widget.get_label()
            setattr(self, name, util.replace_widget(old_widget, toggle_button.ToggleButton(active_pixbuf, inactive_pixbuf, text, clickable=False, default=False)))
            
        # wheel status is special
        self.wheel_status.connect('toggled', self.on_wheel_status_toggled)
            
        # setup the mode buttons
        for mode in ['climbing', 'loading', 'manual', 'shooting']:
            active = util.pixbuf_from_file(mode + '-on.png')
            inactive = util.pixbuf_from_file(mode + '-off.png')
            name =  '%s_mode_button' % mode
            setattr(self, name, util.replace_widget(getattr(self, name), toggle_button.ToggleButton(active, inactive, clickable=True, default=False)))
            
        # setup the fire button
        active = util.pixbuf_from_file('fire-on.png')
        inactive = util.pixbuf_from_file('fire-off.png')
        self.fire_button = util.replace_widget(self.fire_button, image_button.ImageButton(inactive))
        
        # save these for later
        self.fire_button.active_pixbuf = active
        self.fire_button.inactive_pixbuf = inactive
        
        # setup the wheel on button
        active = util.pixbuf_from_file('toggle-on.png')
        inactive = util.pixbuf_from_file('toggle-off.png')
        self.wheel_on_button = util.replace_widget(self.wheel_on_button, toggle_button.ToggleButton(active, inactive, clickable=True, default=False))
        
            
        # attach to the targeter widget
        self.camera_widget.connect('target-update', self.on_target_update)
            
        # connect widgets to pynetworktables
        if self.table is not None:
            
            # don't import this unless we have a table, so we can support running
            # on a laptop without networktables
            import ui.widgets.network_tables as nt
            
            nt.attach_toggle(table, 'Wheel On', self.wheel_on_button)
            nt.attach_toggle(table, 'Wheel OK', self.wheel_status)
            
            nt.attach_chooser_combo(table, 'Autonomous Mode', self.autonomous_chooser)
            
            # other chooser
            widgets = {'Climbing Mode': self.climbing_mode_button, 
                       'Loading Mode': self.loading_mode_button,
                       'Manual Mode': self.manual_mode_button,
                       'Auto Target Mode': self.shooting_mode_button }
            
            nt.attach_chooser_buttons(table, 'Operator Control Mode', widgets)
        
    def on_wheel_status_toggled(self, widget):
        self.update_ready_status()
        
        
    def on_target_update(self, widget, target):
        if target is None:
            self.horizontal_status.set_active(False)
            self.vertical_status.set_active(False)
        else:
            self.horizontal_status.set_active(target.h_ok())
            self.vertical_status.set_active(target.v_ok())
            
        self.update_ready_status()
            
        
    def update_ready_status(self):
        active = self.horizontal_status.get_active() and self.vertical_status.get_active() and self.wheel_status.get_active()
                 
        self.ready_status.set_active(active)   
        if active:
            self.fire_button.set_from_pixbuf(self.fire_button.active_pixbuf)
        else:
            self.fire_button.set_from_pixbuf(self.fire_button.inactive_pixbuf)  
        
    def show_all(self):
        self.window.show_all()
        
    def on_realize(self, widget):
        sz = self.window.get_allocation()
        logger.info('Dashboard window size is %sx%s', sz.width, sz.height)
        
    
    def on_window_destroy(self, widget):
        gtk.main_quit()
        
    def on_cancel_targeting_button_clicked(self, widget):
        self.camera_widget.set_target(None)
        
    #
    # Camera debug settings
    #
    