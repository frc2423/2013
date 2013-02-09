#!/usr/bin/env python2

import math
import os.path
import sys

from optparse import OptionParser
import cv2
import numpy as np

import kwarqs2012cv
import daisycv

from imgproc import CvImg, CvContour, colorspace

print 'Module versions detected:'
print '-> Using Python', sys.version
print '-> Using OpenCV', cv2.__version__
print '-> Using NumPy', np.__version__

def process_image(img):
    cvimg = CvImg(img, colorspace.BGR)
    
    # TODO: image processing goes here
    
    #cvimg.set_colorspace(colorspace.GRAY)
    #cvimg.equalize_hist()
    
    #cvimg.set_colorspace(colorspace.LAB)
    
    #for i, c in enumerate(cvimg.split()):
    #    c.threshold_otsu()
    #    c.show(str(i))
    
    cvimg.show('test')
    
    
    
    
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
                      dest='static_image', default=None,
                      help='Specify an image file to process')
    
    parser.add_option('--ip', dest='ip_address', default='10.24.23.11',
                      help='Specify the IP address of the camera')
    
    parser.add_option('--daisy', dest='daisy', default=False, action='store_true',
                      help='Run the Miss Daisy image processing code')
    
    parser.add_option('--k2012', dest='kwarqs2012', default=False, action='store_true',
                      help='Run the Kwarqs 2012 image processing code')
    
    options, args = parser.parse_args()
    
    # switch between processing functions
    process_fn = process_image
    
    if options.daisy:
        daisy = daisycv.DaisyCv()
        
        def _process_daisy(img):
            cv2.imshow('test', daisy.processImage(img))
        
        process_fn = _process_daisy
    
    elif options.kwarqs2012:
        kwarqs2012 = kwarqs2012cv.Kwarqs2012Cv()
        
        def _process_kwarqs2012(img):
            cv2.imshow('test', kwarqs2012.processImage(img))
        
        process_fn = _process_kwarqs2012
        
    
    if options.static_image is not None:
        print "Opening %s" % options.static_image
        cvimg = CvImg.from_file(options.static_image)
        
        print 'Starting processing. Press ESC to exit'
        cvimg.show('original')
        
        process_fn(cvimg.img)
        
        while True:
            key = 0xff & cv2.waitKey(1)
            if key == 27:
                break        
    else:      
        print "Beginning capture"  
        vc = cv2.VideoCapture('rtsp://%s/axis-media/media.amp' % options.ip_address)
        
        print 'Starting processing. Press ESC to exit, or SPACE to save the current image'
    
        save = False
    
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
    
