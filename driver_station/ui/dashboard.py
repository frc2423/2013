
import gtk

import util
from widgets import targeter, camera_settings, robot_widget, image_button, toggle_button 

from target_detector import target_data

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
        
        'control_notebook',
        
        'climbing_mode_button',
        'loading_mode_button',
        'manual_mode_button',
        'shooting_mode_button',
        
        'wheel_status',
        'ready_status',
        'horizontal_status',
        'vertical_status',
        'target_status',
        
        'fire_button',
        'wheel_on_button',
        'auto_feed_button',
        
        'unused_1',
        'unused_2',
        'unused_3',
        
        'autonomous_chooser',
        'auton_target_high',
        'auton_target_low',
        'auton_target_mid',
        
    ]
    ui_signals = [
        'on_cancel_targeting_button_clicked',
        'on_window_destroy'
    ]
    
    # keep in sync with robot
    MODE_DISABLED       = 1
    MODE_AUTONOMOUS     = 2
    MODE_TELEOPERATED   = 3
    
    def __init__(self, processor, table, competition):
        
        self.processor = processor
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
        
        for name in ['wheel_status', 'ready_status', 'horizontal_status', 'vertical_status', 'target_status']:
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
        self.fire_button.connect('clicked', self.on_fire_clicked)
        
        # save these for later
        self.fire_button.active_pixbuf = active
        self.fire_button.inactive_pixbuf = inactive
        
        # setup the toggle buttons
        active = util.pixbuf_from_file('toggle-on.png')
        inactive = util.pixbuf_from_file('toggle-off.png')
        
        for name in ['wheel_on_button', 'auto_feed_button', 'unused_1', 'unused_2', 'unused_3']:
            setattr(self, name, util.replace_widget(getattr(self, name), toggle_button.ToggleButton(active, inactive, clickable=True, default=False)))
            
        # attach to the targeter widget
        self.camera_widget.connect('target-update', self.on_target_update)
            
        # connect widgets to pynetworktables
        if self.table is not None:
            
            # don't import this unless we have a table, so we can support running
            # on a laptop without networktables
            import ui.widgets.network_tables as nt
            
            nt.attach_toggle(table, 'Wheel On', self.wheel_on_button)
            nt.attach_toggle(table, 'Wheel OK', self.wheel_status)
            
            nt.attach_toggle(table, 'Auto Feeder', self.auto_feed_button)
            
            nt.attach_chooser_combo(table, 'Autonomous Mode', self.autonomous_chooser)
            
            # other chooser
            widgets = {'Climbing Mode': self.climbing_mode_button, 
                       'Loading Mode': self.loading_mode_button,
                       'Manual Mode': self.manual_mode_button,
                       'Auto Target Mode': self.shooting_mode_button }
            
            nt.attach_chooser_buttons(table, 'Operator Control Mode', widgets)
            
            # robot widget
            nt.attach_fn(table, 'Angle', lambda k, v: self.robot_widget.set_angle(v), self.robot_widget)
            nt.attach_fn(table, 'Frisbees', lambda k, v: self.robot_widget.set_frisbee_count(v), self.robot_widget)
            
            # modes
            nt.attach_fn(table, 'Robot Mode', self.on_robot_mode_update, self.window)
            
            # connection listener
            nt.attach_connection_listener(table, self.on_connection_connect, self.on_connection_disconnect, self.window)
       
    def on_connection_connect(self, remote):
        
        # this doesn't seem to actually tell the difference
        if remote.IsServer():
            logger.info("NetworkTables connection to robot detected")
        else:
            logger.info("NetworkTables connection to client detected")
            
        self.processor.start()
        self.camera_widget.start()
        
    def on_connection_disconnect(self, remote):
        if remote.IsServer():
            logger.info("NetworkTables disconnected from robot")
        else:
            logger.info("NetworkTables disconnected from client")
       
    def on_robot_mode_update(self, key, value):
        value = int(value)
        if value == self.MODE_AUTONOMOUS:
            
            self.processor.enable_image_logging()
            
            current_mode = None
            active = self.autonomous_chooser.get_active_iter()
            if active:
                current_mode = self.autonomous_chooser.get_model()[active][0]
            
            logger.info("Robot switched into autonomous mode")
            logger.info("-> Current mode is: %s", current_mode)
            self.control_notebook.set_current_page(0)
            
            # determine the height the user wants
            if self.auton_target_high.get_active():
                logger.info("-> Selecting high target for autonomous mode")
                self.camera_widget.set_target(target_data.location.TOP)
                
            elif self.auton_target_mid.get_active():
                logger.info("-> Selecting middle target for autonomous mode")
                self.camera_widget.set_target(target_data.location.MIDDLE)
                
            elif self.auton_target_low.get_active():
                logger.info("-> Selecting low target for autonomous mode")
                self.camera_widget.set_target(target_data.location.LOW)
            
        elif value == self.MODE_TELEOPERATED:
            
            self.processor.enable_image_logging()
            
            logger.info("Robot switched into teleoperated mode")
            self.control_notebook.set_current_page(1)
            self.camera_widget.set_target(None)
            
        else:
            # don't waste disk space while the robot isn't enabled
            self.processor.disable_image_logging()
            
            logger.info("Robot switched into disabled mode")
            self.control_notebook.set_current_page(0)
        
            
        
        
    def on_wheel_status_toggled(self, widget):
        self.update_ready_status()
        
        
    def on_target_update(self, widget, target):
        if target is None:
            self.horizontal_status.set_active(False)
            self.vertical_status.set_active(False)
            self.target_status.set_active(False)
        else:
            self.horizontal_status.set_active(target.h_ok())
            self.vertical_status.set_active(target.v_ok())
            self.target_status.set_active(True)
            
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
        
    def on_fire_clicked(self, widget):
        
        # presumably when the user fires, they want to remain stationary
        self.camera_widget.set_target(None)
        
        if self.table is not None:
            self.table.PutNumber(u'Fire', 5)
        