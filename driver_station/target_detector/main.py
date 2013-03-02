#!/usr/bin/env python2

import math
import os.path
import sys
import time

from optparse import OptionParser
import cv2
import numpy as np

from imgproc import CvImg, CvContour, colorspace

print 'Module versions detected:'
print '-> Using Python', sys.version
print '-> Using OpenCV', cv2.__version__
print '-> Using NumPy', np.__version__


def process_static_images(path, process_fn):
    
    if not os.path.isdir(path):
        images = [path]
    else:
        images = []
        for path, dirs, files in os.walk(path):
            images += [os.path.join(path, f) for f in files] 
    
    idx = 0
    
    while idx < len(images) and idx >= 0:
        
        image = images[idx]
        
        print "Opening %s" % image
        
        try:
            cvimg = CvImg.from_file(image)
        except IOError as e:
            print "Error opening %s: %s" % (path, e)
            idx += 1
            continue
        
        print 'Starting processing. Press ESC to exit, ENTER for next image'
        cvimg.show('original')
        
        process_fn(cvimg.img)
        
        while True:
            code = cv2.waitKey(1)
            key = 0xff & code
            if key == ord('\n') or key == ord('\r'):
                idx += 1
                break
            elif key == 27:
                idx = len(images)
                break
            # right key
            elif key == 83 or code == 0x270000:
                idx += 1
                break
            
            # left key
            elif key == 81 or code == 0x250000:
                idx -= 1
                break
    
def user_save_image(img):
    
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


if __name__ == '__main__':
    
    parser = OptionParser()
    
    parser.add_option('-i',
                      dest='static_images', default=None,
                      help='Specify an image file (or directory) to process')
    
    parser.add_option('--ip', dest='ip_address', default='10.24.23.11',
                      help='Specify the IP address of the camera')
    
    parser.add_option('--robot-ip', dest='robot_ip', default=None,
                      help='Specified the IP address of the robot')
    
    parser.add_option('--daisy', dest='daisy', default=False, action='store_true',
                      help='Run the Miss Daisy image processing code')
    
    parser.add_option('--k2012', dest='kwarqs2012', default=False, action='store_true',
                      help='Run the Kwarqs 2012 image processing code')
    
    parser.add_option('--save', dest='save', default=None)
    
    options, args = parser.parse_args()
    
    # switch between processing functions
    process_fn = None
    
    table = None
    
    if options.robot_ip is not None:
        
        from pynetworktables import NetworkTable
        
        NetworkTable.SetIPAddress(options.robot_ip)
        NetworkTable.SetClientMode()
        NetworkTable.Initialize()
        
        table = NetworkTable.GetTable(u'SmartDashboard')
    
    if options.daisy:
        
        import daisycv
        
        daisy = daisycv.DaisyCv()
        
        def _process_daisy(img):
            cv2.imshow('result', daisy.processImage(img))
        
        process_fn = _process_daisy
    
    elif options.kwarqs2012:
        
        import kwarqs2012cv
        
        kwarqs2012 = kwarqs2012cv.Kwarqs2012Cv()
        
        def _process_kwarqs2012(img):
            cv2.imshow('result', kwarqs2012.processImage(img))
        
        process_fn = _process_kwarqs2012
        
    else:
        import kwarqs2013cv
        
        detector = kwarqs2013cv.TargetDetector(table)
        
        def _process_kwarqs2013(img):
            cv2.imshow('result', detector.processImage(img))
        
        process_fn = _process_kwarqs2013
    
    
    
    if options.static_images is not None:        
        process_static_images(options.static_images, process_fn)
               
    else:      
        
        # TODO: Need to determine best mechanisms to use for
        # retry, or what happens when the camera cannot be talked 
        # to? Ideally, if we use OpenCV's RTSP implementation, we
        # will end up with a higher quality image stream than what
        # SmartDashboard can provide us.. but, how robust is it?
        
        # TODO: How to integrate this with the SmartDashboard?
        #        -> in particular, what kind of UI should we provide?
        
        # TODO: Exception handling in case something goes awry
        # -> Need to restart processing if this crashes
        
        # TODO: What other things are required for robustness?
        
        # TODO: Integration with pynetworktables
        
        # TODO: Run detection on a whole directory of images, and 
        # print out the results or something to that effect
        
        # TODO: Given the current shooter angle, put something on the
        #       image that represents the possible vector where it'll be
        
        print "Beginning capture"  
        #vc = cv2.VideoCapture('rtsp://%s/axis-media/media.amp' % options.ip_address)
        vc = cv2.VideoCapture('http://%s/mjpg/video.mjpg' % options.ip_address)
        
        print 'Starting processing. Press ESC to exit, or SPACE to save the current image'
    
        save = False
        
        tm = time.time()
    
        while True:
            retval, img = vc.read()
            if retval:
                
                if save:
                    user_save_image(img)
                    save = False
                
                process_fn(img)
            else:
                print "No image acquired, exiting!"
                break
            
            key = 0xff & cv2.waitKey(1)
            if key == 27:
                break
            
            if key == ord(' '):
                save = True
        
    cv2.destroyAllWindows()
    print "Done."
    
