#!/usr/bin/env python2

import datetime
import os.path
import time
import threading

import cv2
import gtk
import numpy as np

from imgproc import CvImg, CvContour, colorspace
import kwarqs2013cv

import logging
from common import logutil, settings
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
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
    
    def initialize(self, options, camera_widget):
        
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
            
            self.images.sort()
        
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
        

    @logutil.exception_decorator(logger)
    def _static_processing(self):
        
        logger.info("Static processing thread starting")
        idx = -1
        
        # resume processing with the last image the user looked at
        last_img = settings.get('processing/last_img', None)
        for i, image_name in enumerate(self.images):
            if image_name == last_img:
                self.idx = i
                break 
        
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
                
                try:
                    target_data = self.detector.processImage(cvimg.img)
                except:
                    logutil.log_exception(logger, 'error processing image')
                else:
                    settings.set('processing/last_img', image_name)
                    settings.save()
                    
                    logger.info('Finished processing')
                
                    # note that you cannot typically interact with the UI
                    # from another thread -- but this function is special
                    self.camera_widget.set_target_data(target_data)
            
        logger.info("Static processing thread exiting")

        
    def _initialize_live(self):
        vc = cv2.VideoCapture()
        
        vc.set(cv2.cv.CV_CAP_PROP_FPS, 1)
        
        logger.info('Connecting to %s' % self.camera_ip)
        if not vc.open('http://%s/mjpg/video.mjpg' % self.camera_ip):
            logger.error("Could not connect")
            return
        
        logger.info('Connected!')
        return vc
            

    @logutil.exception_decorator(logger)
    def _live_processing(self):
        
        logger.info("Live processing thread starting")
        
        while True:
            
            # check for exit condition
            with self.lock:
                if self.do_stop:
                    break
            
            # open the video capture device
            vc = self._initialize_live()
            
            if vc is None:
                continue
        
            last_log = 0
            exception_occurred = False
            
            # allocate a buffer for reading
            h = vc.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
            w = vc.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
            
            capture_buffer = np.empty(shape=(h, w, 3), dtype=np.uint8)
            
            while True:
            
                # check for exit condition
                with self.lock:
                    if self.do_stop:
                        break
                
                #
                # Read the video frame
                #
                
                retval, img = vc.read(capture_buffer)
                
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
                
                    #
                    # Process the image
                    #
                    
                    try:
                        target_data = self.detector.processImage(img)
                    except:
                        # if it happened once, it'll probably happen again. Don't flood
                        # the logfiles... 
                        if not exception_occurred:
                            logutil.log_exception(logger, 'error processing image')
                            exception_occurred = True
                        self.camera_widget.set_error(img)
                        
                    else:
                        if exception_occurred:
                            logger.info("Processing resumed, no more errors.")
                            exception_occurred = False
                        
                        # note that you cannot typically interact with the UI
                        # from another thread -- but this function is special
                        self.camera_widget.set_target_data(target_data)
                                        
                else:
                    if last_log == 0: 
                        logger.error("Not able to connect to camera, retrying")
                    else:
                        logger.error("Camera disconnected, retrying")
                        
                    self.camera_widget.set_no_camera()
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
        
    @logutil.exception_decorator(logger)
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
    
