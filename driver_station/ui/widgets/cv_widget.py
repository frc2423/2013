
import cairo
import glib
import gtk

import cv2
import numpy as np

import threading


class CvWidget(gtk.DrawingArea):
    '''
        This is a class to show an OpenCV image in a GTK widget
        
        Initialized to a fixed size for now
        
        One way that you could do this is by just copying the OpenCV images
        to a pixbuf... but that would involve a lot of memory allocation and
        unnecessary copies. The way this works is we have a buffer stored
        that has a cairo surface associated with it, and we copy onto that
        and draw it using the expose event for the widget.
    '''
    
    
    def __init__(self, fixed_size):
        
        gtk.DrawingArea.__init__(self)
        
        self._fixed_size = fixed_size
        w, h = fixed_size
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
        self.buffer = np.frombuffer(self.surface, dtype=np.uint8)
        
        self.buffer.shape = (h, w, 4) # numpy w/h are switched
        self.buffer.fill(0x00)
        
        self.set_size_request(w, h)
        self.connect_after('expose-event', self.on_expose)
        
        # TODO: should we turn off double buffering?
        
    def on_expose(self, widget, event):
        '''
            This draws the contents of the surface onto the widget.
        '''
        
        cr = event.window.cairo_create()
        cr.set_source_surface(self.surface)
        
        # TODO: only draw damaged sections, instead of the whole image
        
        w, h = self._fixed_size
        
        # tell cairo to draw the image onto the context
        cr.line_to(0,0)
        cr.line_to(w,0)
        cr.line_to(w,h)
        cr.line_to(0,h)
        cr.line_to(0,0)
        
        cr.fill()
        cr.stroke()
    
    
    def set_from_np(self, img):
        '''Sets the contents of the image from a numpy array'''
        
        # TODO: how does locking work out here?
        
        # if resize needed, then do it
        
        # now copy it and convert to the right format
        cv2.cvtColor(img, cv2.COLOR_BGR2BGRA, self.buffer)
        
        # .. and invalidate?
        self.queue_draw()
        #glib.idle_add(self.queue_draw)
        
    