
import cv2
import numpy as np

from util import cvt_colorspace, colorspace


class CvImg(object):
    '''
        Wrapper object to manage an numpy array used for OpenCV
    '''
    
    __slots__ = ['img', 'colorspace']
    
    @staticmethod
    def from_file(filename):
        img = cv2.imread(filename)
        if img is not None:
            return CvImg(img, colorspace.BGR)
        
        raise IOError("Could not open '%s'" % filename)
    
    def __init__(self, img, colorspace, original=None):
        self.img = img
        self.colorspace = colorspace
        
        # TODO: If we need to keep track of offsets or stuff, patch them in here
        if original is not None:
            pass
        
    def clone(self):
        return CvImg(self.img.copy(), self.colorspace, self)
    
    def dilate(self, param, shape=cv2.MORPH_RECT):
        kernel = cv2.getStructuringElement(shape, (param,param))
        cv2.dilate(self.img, kernel, self.img)
    
    def erode(self, param, shape=cv2.MORPH_RECT):
        kernel = cv2.getStructuringElement(shape, (param,param))
        cv2.erode(self.img, kernel, self.img)
    
    def equalize_hist(self):
        cv2.equalizeHist(self.img, self.img)
        
    def find_contours(self, copy=True):
        ''' This function uses the image data to do stuff, so specify 
            copy=True if you intend to reuse the data for something'''
        if copy:
            img = self.img.copy()
        else:
            img = self.img
        contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
        return contours
        
    def save(self, filename):
        cv2.imwrite(filename, self.img)
        
    def set_colorspace(self, colorspace):
        if self.colorspace != colorspace:
            self.img = cvt_colorspace(self.img, self.colorspace, colorspace)
            self.colorspace = colorspace
        
    def show(self, window_name):
        cv2.imshow(window_name, self.img)
        
    def split(self):
        return [CvImg(c, colorspace.GRAY) for c in cv2.split(self.img)]
        
    def threshold_otsu(self):
        cv2.threshold(self.img, 0, 0xff, cv2.THRESH_BINARY | cv2.THRESH_OTSU, self.img)
        
