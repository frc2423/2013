#!/usr/bin/env python2

import datetime
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
    '''
        This class manages the image processing stuff. It determines what
        actions to take, and then performs them on another thread.
        
        The actual image processing takes place in a different class. That 
        class processes the image, and then returns a dictionary that has
        targeting information in it.
    '''
    
    def __init__(self):
        self.detector = kwarqs2013cv.TargetDetector()
    
    def initialize(self, options, camera_widget):
        
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
        self.do_stop = False
        self.do_refresh = False
        
        self.camera_ip = options.camera_ip
        self.camera_widget = camera_widget
        
        self.img_logger = None
        
        if options.log_images:
            self.img_logger = ImageLogger(options.log_dir)
        
        # detect live or static processing
        if options.static_images is not None:
            self._initialize_static(options)
            thread_fn = self._static_processing
        else:
            thread_fn = self._live_processing
            
        self.thread = threading.Thread(target=thread_fn)
        self.thread.setDaemon(True)
        
        
    def start(self):
        if self.img_logger is not None:
            self.img_logger.start()
        self.thread.start()
        
    def stop(self):
        self.do_stop = True
        with self.condition:
            self.condition.notify()
            
        self.thread.join()
        
        if self.img_logger is not None:
            self.img_logger.stop()
        
    def refresh(self):
        with self.condition:
            self.do_refresh = True
            self.condition.notify()
        
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
        
        def _on_button_pressed(widget, event):
            widget.grab_focus()
        
        # must be able to get focus to receive keyboard events
        self.camera_widget.set_can_focus(True)
        self.camera_widget.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        
        self.camera_widget.grab_focus()
        self.camera_widget.connect('key-press-event', _on_key_press)
        self.camera_widget.connect('button-press-event', _on_button_pressed)
        

        
    def _static_processing(self):
        
        logger.info("Static processing thread starting")
        idx = -1
        while True:
        
            with self.condition:
                
                # wait until the user hits a key
                while idx == self.idx and not self.do_stop and not self.do_refresh:
                    self.condition.wait()
                
                if self.do_stop:
                    break
                
                idx = self.idx
                self.do_refresh = False
                    
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
                
                target_data = self.detector.processImage(cvimg.img)
                logger.info('Finished processing')
                
                # note that you cannot typically interact with the UI
                # from another thread -- but this function is special
                self.camera_widget.set_target_data(target_data)
            
        logger.info("Static processing thread exiting")

        
    def _initialize_live(self):
        self.vc = cv2.VideoCapture()
        
        self.vc.set(cv2.cv.CV_CAP_PROP_FPS, 1)
        
        logger.info('Connecting to %s' % self.camera_ip)
        self.vc.open('http://%s/mjpg/video.mjpg' % self.camera_ip)
    
        logger.info('Connected!')

            
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
        
        self._initialize_live()
        
        last_log = 0
    
        while True:
        
            with self.lock:
                if self.do_stop:
                    break
            
            retval, img = self.vc.read()
            if retval:
                
                # log images to directory
                if self.img_logger is not None:
                    tm = time.time()
                    diff = tm - last_log
                    if diff >= 1:
                        self.img_logger.log_image(img)
                        
                        # adjust for possible drift
                        if diff > 1.5:
                            last_log = tm
                        else:
                            last_log += 1
                
                target_data = self.detector.processImage(img)
                
                # note that you cannot typically interact with the UI
                # from another thread -- but this function is special
                self.camera_widget.set_target_data(target_data)
            #else:
                #self.camera_widget.set_no_stream()
                
            else:
                # TODO: Fix this 
                print "No image acquired, exiting!"
                break
            
        logger.info("Static processing thread exiting")


class ImageLogger(object):

    def __init__(self, logdir):
        self.logdir = logdir
        self.has_image = False
        self.do_stop = False
        
        self.condition = threading.Condition()
        self.thread = threading.Thread(target=self._log_thread)
        
    def log_image(self, image):
        h, w = image.shape[:2]
        datestr = datetime.datetime.now().strftime('%Y-%m-%d %H%M-%S-%f')
        filename = '%s@%sx%s.png' % (datestr, w, h)
        filename = os.path.join(self.logdir, filename)
        
        with self.condition:
            self.has_image = True
            
            # TODO: does making a copy here matter?
            self.img = image.copy()
            self.img_filename = filename
            
            self.condition.notify()
            
    def start(self):
        self.thread.start()
        
    def stop(self):
        with self.condition:
            self.do_stop = True
            self.condition.notify()
            
        self.thread.join()
        
    def _log_thread(self):
        
        while True:
            with self.condition:
                
                if self.do_stop:
                    break
                
                while not self.has_image and not self.do_stop:
                    self.condition.wait()
                    
                # if there's an image queued up, then we want to
                # write it out before exiting
                if not self.has_image:
                    continue
                
                img = self.img
                img_filename = self.img_filename
                self.has_image = False
                
            logger.debug('Writing image to %s' % img_filename)
            cv2.imwrite(img_filename, img)
            


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
    
