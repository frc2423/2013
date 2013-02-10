
import cv2
import numpy as np

from imgproc import CvImg, colorspace

class TargetDetector(object):
    
    def __init__(self):
        pass
    
    def processImage(self, img):
        
        #cvimg = CvImg(img, colorspace.BGR)
        
        # adjusts contrast (less than 1 is darker)
        contrast = 1
        
        # brightness
        brightness = 0
        #brightness = -100
        
        ones = np.ones(img.shape, img.dtype)
        zeros = np.zeros(img.shape, img.dtype)
        
        # adjusts brightness
        img = cv2.add(img, np.array((brightness,)))
        
        # adjusts contrast
        img = cv2.multiply(img, ones, scale=contrast)
        
        
        l, u, v = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
        
        cv2.threshold(u, 20, 255, type=cv2.THRESH_BINARY_INV, dst=u)
        #u = np.invert(u)
        
        cv2.imshow('l', l)
        cv2.imshow('u', u)
        cv2.imshow('v', v)
        
        return img
    