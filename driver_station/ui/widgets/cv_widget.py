
import gtk

class CvWidget(gtk.Image):
    '''
        This is a class to show an OpenCV image in a GTK widget
        
        
    '''
    
    def __init__(self, fixed_size=None):
        
        gtk.Image.__init__(self)
        
        self._fixed_size = fixed_size
        if fixed_size is not None:
            w, h = fixed_size
            self._pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, w, h)


    def set_from_np(self, np):
        '''Sets the contents of the image from a numpy array'''
        
        # if resize needed, then do it
        
        # now draw the buffer onto the pixbuf
        
        # .. and invalidate?
    