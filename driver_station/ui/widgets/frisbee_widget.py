
import os

import gtk

import ui.util

class FrisbeeWidget(gtk.DrawingArea):
    
    def __init__(self, table):
        gtk.DrawingArea.__init__(self)
        
        self.table = table
    
        # TODO: set up a listener or something.. 
        
        # load the frisbee pngs
        
        self.gray_frisbee = gtk.gdk.pixbuf_new_from_file(os.path.join(ui.util.data_dir, 'gray_frisbee.png'))
        self.red_frisbee = gtk.gdk.pixbuf_new_from_file(os.path.join(ui.util.data_dir, 'red_frisbee.png'))
        
        # set the
        self.count = 1
        self.max_frisbees = 4
        
        self.set_size_request(self.gray_frisbee.get_width(), self.gray_frisbee.get_height()* self.max_frisbees)
        
        self.connect('expose-event', self.on_expose)
        
    def set_frisbee_count(self, count):
        self.count = count
        self.queue_draw()
        
    def on_expose(self, widget, event):
        
        h = self.gray_frisbee.get_height()
        
        for i in xrange(self.max_frisbees):
            if i < self.count:
                # draw full frisbee
                event.window.draw_pixbuf(None, self.red_frisbee, 0, 0, 0, h*(self.max_frisbees-i))
            else:
                # draw empty frisbee
                event.window.draw_pixbuf(None, self.gray_frisbee, 0, 0, 0, h*(self.max_frisbees-i))
                
        
