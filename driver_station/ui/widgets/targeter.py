
import glib
import gtk

from cv_widget import CvWidget

import threading

import target_detector.target_data

import logging
from common import logutil
logger = logging.getLogger(__name__)


class Targeter(CvWidget):
    
    TOP = target_detector.target_data.location.TOP
    LMIDDLE = target_detector.target_data.location.LMIDDLE
    RMIDDLE = target_detector.target_data.location.RMIDDLE
    MIDDLE = target_detector.target_data.location.MIDDLE
    LOW = target_detector.target_data.location.LOW
    
    def __init__(self, fixed_size):
        CvWidget.__init__(self, fixed_size)
        
        self.lock = threading.Lock()
        self.active_target = None
        self.target_location = None
        
        # don't set this right away, wait for 3 seconds -- otherwise the user 
        # might think there's an error when there really isn't one
        # -> if True/False, set camera/error appropriately. show blank if None
        self.show_error = None
        glib.timeout_add_seconds(3, self._no_camera_timer)
        
        # enable mouse clicks
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.on_button_click)
        
    def _no_camera_timer(self):
        '''Called after N seconds starting up, to see if we found a camera yet'''
        with self.lock:
            if self.show_error is None:
                self.show_error = True
                self.queue_draw()
        
    def on_button_click(self, widget, event):
        '''Called on mouse click'''
        x = event.x * self.zoom
        y = event.y * self.zoom
        
        with self.lock:
            for target in self.targets:
                if not target.intersects(x, y):
                    continue
                
                self.active_target = target
                self.target_location = target.location
                
                self.queue_draw()
                break
        
    def on_expose(self, widget, event):
        CvWidget.on_expose(self, widget, event)
        
        with self.lock:
            active_target = self.active_target
            show_error = self.show_error
        
        # if there is an error, draw a warning icon 
        if show_error == True:
            pixbuf = self.render_icon(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)
            
            # center it
            ww, wh = event.window.get_size()
            
            pw = pixbuf.get_width()
            ph = pixbuf.get_height()
            
            
            x = int(ww/2.0 - pw/2.0)
            y = int(wh/2.0 - ph/2.0)
            
            event.window.draw_pixbuf(None, pixbuf, 0, 0, x, y)
        
            
        if active_target is None:
            return
        
        
        # this needs improvement
        if active_target is None:
            return
        
        cxt = event.window.cairo_create()
        if self.zoom != 1:
            scale = 1.0/self.zoom
            cxt.scale(scale, scale)
        
        polygon = self.active_target.polygon
            
        self.draw_contour(cxt, polygon)
        
        
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
        
    def set_error(self, img=None):
        '''Causes an error icon to be shown'''
        with self.lock:
            self.show_error = True
            self.active_target = None
            
        self.set_from_np(img)
        
    def set_target_data(self, target_data, error=False):
        '''This is called from another thread, so be careful'''
        
        img, targets, cat_tgts = target_data
        
        # ok, try to select the correct target
        
        # Note: if we lose track of the target for a short period of time, 
        # that's ok. We hold onto the last known target preference for a 
        # period of time and restore it if the robot saw it
        
        # todo: figure out what the period of time is
        
        
        with self.lock: 
            try:
                self.show_error = error
                self.targets = targets
                
                if self.target_location is not None:
                    target = None
                    
                    if self.target_location == self.TOP:
                        tops = cat_tgts['top']
                        
                        # prefer the highest target
                        if len(tops) != 0:
                            target = tops[0]
                        
                    elif self.target_location == self.LOW:
                        lows = cat_tgts['low']
                        
                        # prefer the highest target
                        if len(lows) != 0:
                            target = lows[0]
                            
                    else: # middle target is more complex
                        
                        # middle targets are ordered left to right
                        
                        mids = cat_tgts['mid']
                        if len(mids) != 0:
                        
                            if self.target_location == self.LMIDDLE:
                                # prefer lmiddle/middle
                                for t in mids:
                                    if t.location == self.LMIDDLE:
                                        target = t
                                        break
                                    elif t.location == self.MIDDLE:
                                        target = t
                                        break
                                
                            elif self.target_location == self.RMIDDLE:
                                # prefer rmiddle/middle
                                for t in mids:
                                    if t.location == self.RMIDDLE:
                                        target = t
                                        break
                                    elif t.location == self.MIDDLE:
                                        target = t
                                        break
                            
                            elif self.target_location == self.MIDDLE:
                                # prefer the highest
                                mids.sort(key=lambda tgt: tgt.y, reverse=True)
                                target = mids[0]
                    
                    self.active_target = target
            except:
                self.active_target = None
                self.show_error = True
                logutil.log_exception(logger, 'Error calculating targeting data!')
        
        self.set_from_np(img)


