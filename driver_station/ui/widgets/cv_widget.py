
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
    
    
    def __init__(self, fixed_size=None):
        gtk.DrawingArea.__init__(self)
        
        self._fixed_size = fixed_size
        
        if fixed_size is not None:
            w, h = fixed_size
            
            self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
            self.buffer = np.frombuffer(self.surface, dtype=np.uint8)
            self.resize_buffer = np.empty(shape=(h,w,3), dtype=np.uint8)
            
            self.buffer.shape = (h, w, -1) # numpy w/h are switched
            self.buffer.fill(0x00)
        
            self.set_size_request(w, h)
            
        self.connect('expose-event', self.on_expose)
        
        # TODO: should we turn off double buffering?
        
    def on_expose(self, widget, event):
        '''
            This draws the contents of the surface onto the widget.
        '''
        
        if self.surface is None:
            return
        
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
        h, w, c = img.shape
        if w != self._fixed_size[0] or h != self._fixed_size[1]:
            cv2.resize(img, self._fixed_size, self.resize_buffer)
            src = self.resize_buffer
        else:
            src = img
        
        # now copy it to the buffer and convert to the right format
        cv2.cvtColor(src, cv2.COLOR_BGR2RGBA, self.buffer)
        
        # .. and invalidate?
        self.queue_draw()
        
    