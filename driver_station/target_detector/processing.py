#!/usr/bin/env python2

import os.path
import time
import threading

import cv2
import gtk

from imgproc import CvImg, CvContour, colorspace
import kwarqs2013cv

import logging
logger = logging.getLogger(__name__)


class ImageProcessor(object):
    
    def __init__(self, options, camera_widget):
        
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
        self.do_stop = False
        
        self.detector = kwarqs2013cv.TargetDetector(None)
        self.camera_ip = options.camera_ip
        self.camera_widget = camera_widget
        
        # detect live or static procesing
        if options.static_images is not None:
            self._initialize_static(options)
            thread_fn = self._static_processing
        else:
            thread_fn = self._live_processing
            
        self.thread = threading.Thread(target=thread_fn)
        self.thread.setDaemon(True)
        
        
    def start(self):
        self.thread.start()
        
    def stop(self):
        self.do_stop = True
        with self.condition:
            self.condition.notify()
            
        self.thread.join()
        
    def _initialize_static(self, options):
        
        path = options.static_images
        self.idx = 0
        
        if not os.path.exists(path):
            logger.error("'%s' does not exist!" % path)
            raise RuntimeError()
        
        if not os.path.isdir(path):
            self.images = [path]
        else:
            self.images = []
            for path, dirs, files in os.walk(path):
                self.images += [os.path.join(path, f) for f in files] 
        
        # setup the key handler
        def _on_key_press(widget, event):
            if event.keyval == gtk.keysyms.Left:
                if self.idx > 0:
                    with self.condition:
                        self.idx -= 1
                        self.condition.notify()
            elif event.keyval == gtk.keysyms.Right:
                if self.idx < len(self.images):
                    with self.condition:
                        self.idx += 1
                        self.condition.notify()
            elif event.keyval == gtk.keysyms.Escape:
                gtk.main_quit()
            
            # return True otherwise we might lose focus
            return True
        
        # must be able to get focus to receive keyboard events
        self.camera_widget.set_can_focus(True)
        self.camera_widget.grab_focus()
        self.camera_widget.connect('key-press-event', _on_key_press)
        

        
    def _static_processing(self):
        
        logger.info("Static processing thread starting")
        idx = -1
        while True:
        
            with self.condition:
                
                # wait until the user hits a key
                while idx == self.idx and not self.do_stop:
                    self.condition.wait()
                
                if self.do_stop:
                    break
                
                idx = self.idx
                    
            # if the index is valid, then process an image
            if idx < len(self.images) and idx >= 0:
                
                image_name = self.images[idx]
                
                logger.info("Opening %s" % image_name)
                
                try:
                    cvimg = CvImg.from_file(image_name)
                except IOError as e:
                    logger.error("Error opening %s: %s" % (image_name, e))
                    self.idx += 1
                    continue
                
                img = self.detector.processImage(cvimg.img)
                logger.info('Finished processing')
                
                # note that you cannot typically interact with the UI
                # from another thread -- but this function is special
                self.camera_widget.set_from_np(img)
            
        logger.info("Static processing thread exiting")
            
    def _live_processing(self):
        
        # TODO: Need to determine best mechanisms to use for
        # retry, or what happens when the camera cannot be talked 
        # to? Ideally, if we use OpenCV's RTSP implementation, we
        # will end up with a higher quality image stream than what
        # SmartDashboard can provide us.. but, how robust is it?
        
        # TODO: How to integrate this with the SmartDashboard?
        #        -> in particular, what kind of UI should we provide?
        
        # TODO: Exception handling in case something goes awry
        # -> Need to restart processing if this crashes
        # -> Need to log errors too
        
        # TODO: What other things are required for robustness?
        
        # TODO: Integration with pynetworktables
        
        # TODO: Run detection on a whole directory of images, and 
        # print out the results or something to that effect
        
        # TODO: Given the current shooter angle, put something on the
        #       image that represents the possible vector where it'll be
        
        logger.info("Live processing thread starting")
        vc = cv2.VideoCapture()
        
        vc.set(cv2.cv.CV_CAP_PROP_FPS, 5)
        
        logger.info('Connecting to %s' % self.camera_ip)
        vc.open('http://%s/mjpg/video.mjpg' % self.camera_ip)
    
        logger.info('Connected!')
    
        save = False
        
        tm = time.time()
    
        while True:
        
            with self.lock:
                if self.do_stop:
                    break
            
            retval, img = vc.read()
            if retval:
                img = self.detector.processImage(img)
                
                # note that you cannot typically interact with the UI
                # from another thread -- but this function is special
                self.camera_widget.set_from_np(img)
            #else:
                #self.camera_widget.set_no_stream()
                
            else:
                # TODO: Fix this 
                print "No image acquired, exiting!"
                break
            
        logger.info("Static processing thread exiting")


def user_save_image(img):
    # TODO: make this work in new framework
    
    # TODO: the image freezes while this is waiting for input. Fix that. 
    
    # Hehe. 
    timg = img.copy()
    h, w = timg.shape[:2]
    cv2.putText(timg, 'OH SNAP!', (w/6,h/2), cv2.FONT_HERSHEY_COMPLEX, 3, (255,255,255), 4)
    
    cv2.imshow('test', timg)
    cv2.waitKey(1)
    
    while True:
        filename = raw_input('Save to .png: ')
    
        if filename == '':
            continue
    
        if not filename.endswith('.png'):
            filename = filename + '.png'
            
        filename = os.path.abspath(filename)
    
        if os.path.exists(filename):
            overwrite = False
            while True:
                yn = raw_input("'%s' exists! Overwrite? [y/n] " % filename).lower()
                if yn == 'y':
                    overwrite = True
                    break
                elif yn == 'n':
                    break
                
            if not overwrite:
                continue
    
        if cv2.imwrite(filename, img):
            print "Image saved to '%s'" % filename
            break
        else:
            print "Error writing to '%s'!" % filename
    
