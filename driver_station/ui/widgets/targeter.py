
import gtk
from cv_widget import CvWidget

class Targeter(CvWidget):
    
    def __init__(self, fixed_size):
        CvWidget.__init__(self, fixed_size)
        self.active_target = None
        
        # enable mouse clicks
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.on_button_click)
        
        
    def on_button_click(self, widget, event):
        '''Called on mouse click'''
        
        for target in self.targets:
            if not target.intersects(event.x, event.y):
                continue
            
            # TODO: invalidate only a specific region
            self.active_target = target
            self.queue_draw()
            break
        
    def on_expose(self, widget, event):
        CvWidget.on_expose(self, widget, event)
        
        # this needs improvement
        if self.active_target is None:
            return
        
        cxt = event.window.cairo_create()
        self.draw_contour(cxt, self.active_target.polygon)
        
        
    def draw_contour(self, cxt, contour):    
        
        # TODO: improve this too
            
        x, y = contour[0,0]
        cxt.move_to(int(x), int(y))
        
        for x,y in contour[1:,0,:]:
            cxt.line_to(int(x), int(y))
            
        # close it off
        cxt.close_path()
        
        # fill it in
        cxt.set_source_rgb(0, 1, 0)
        cxt.fill_preserve()
        
        # outline it
        cxt.set_source_rgb(1, 1, 0)
        cxt.set_line_width(3)
        cxt.stroke()
        
    def set_target_data(self, target_data):
        '''This is called from another thread, so be careful'''
        
        img, targets, cat_tgts = target_data
        
        print len(targets), cat_tgts
        self.targets = targets
        self.cat_tgts = cat_tgts
        
        # TODO: pass on active target to new targets
        self.active_target = None
        
        self.set_from_np(img)