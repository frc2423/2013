
import gtk
import gobject

from image_button import ImageButton

class ToggleButton(gtk.HBox):
    '''Similar to a GTK CheckButton, but different
    
        .. seems like they should already have this implemented, but I can't
        find one. 
    '''
    
    __gsignals__ = {
        'toggled': (gobject.SIGNAL_ACTION, gobject.TYPE_NONE, ()), 
    }
    
    def __init__(self, active_pixbuf, inactive_pixbuf, label=None, clickable=False, default=False):
        gtk.HBox.__init__(self)
        
        self.set_spacing(5)
        
        self.image_button = ImageButton()
        self.pack_start(self.image_button, False, False)
        
        self.active = not default
        self.active_pixbuf = active_pixbuf
        self.inactive_pixbuf = inactive_pixbuf
        
        if clickable:
            self.image_button.connect('clicked', self.on_clicked)
        
        if label is not None:
            self.label = gtk.Label(label)
            self.pack_start(self.label, False, False)
            
        self.set_active(default)
        
    def on_clicked(self, widget):
        self.set_active(not self.active)
    
    def get_active(self):
        return self.active
        
    def set_active(self, active):
        if active != self.active:
            self.active = active
            if active:
                self.image_button.set_from_pixbuf(self.active_pixbuf)
            else:
                self.image_button.set_from_pixbuf(self.inactive_pixbuf)
                
            self.emit('toggled')
            
gobject.type_register(ToggleButton)
