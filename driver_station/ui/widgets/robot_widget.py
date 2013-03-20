
import os

import gtk

import ui.util

class RobotWidget(gtk.DrawingArea):
    
    def __init__(self, table):
        gtk.DrawingArea.__init__(self)
        
        self.table = table
    
        # TODO: set up a listener or something.. 
        
        # load the frisbee pngs
        
        self.robot = ui.util.pixbuf_from_file('robot.png')
        self.gray_frisbee = ui.util.pixbuf_from_file('gray_frisbee.png')
        self.red_frisbee = ui.util.pixbuf_from_file('red_frisbee.png')
        
        # setup the frisbee data
        # -> TODO
        self.count = 1
        self.max_frisbees = 4
        
        # size request
        self.set_size_request(self.robot.get_width(), self.robot.get_height())
        
        self.connect('expose-event', self.on_expose)
        
    def set_frisbee_count(self, count):
        self.count = count
        self.queue_draw()
        
    def on_expose(self, widget, event):
        
        event.window.draw_pixbuf(None, self.robot, 0, 0, 0, 0)
        
        return
        
        # TODO: draw frisbees
        h = self.gray_frisbee.get_height()
        
        for i in xrange(self.max_frisbees):
            if i < self.count:
                # draw full frisbee
                event.window.draw_pixbuf(None, self.red_frisbee, 0, 0, 0, h*(self.max_frisbees-i))
            else:
                # draw empty frisbee
                event.window.draw_pixbuf(None, self.gray_frisbee, 0, 0, 0, h*(self.max_frisbees-i))
                
        
