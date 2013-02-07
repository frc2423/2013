
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
    
    width = property(lambda self: self.img.shape[1])
    height = property(lambda self: self.img.shape[0])
    channels = property(lambda self: self.img.shape[2])
    
    def __init__(self, img, colorspace, original=None):
        self.img = img
        self.colorspace = colorspace
        
        # TODO: If we need to keep track of offsets or stuff, patch them in here
        if original is not None:
            pass
        
    def bitwise_and(self, other):
        cv2.bitwise_and(self.img, other.img, dst=self.img)
        return self
        
    def clone(self):
        return CvImg(self.img.copy(), self.colorspace, self)
    
    def clone_zeroed(self):
        return CvImg(np.zeros(self.img.shape, self.img.dtype), self.colorspace, self)
    
    def draw_contours(self, contours, color, thickness=1):
        cv2.drawContours(self.img, contours, -1, color, thickness=thickness)
    
    def draw_contour(self, contour, color, thickness=1):
        cv2.drawContours(self.img, [contour], -1, color, thickness=thickness)
        
    def draw_point(self, pt, radius, color):
        cv2.circle(self.img, pt, radius, color)
    
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
        
    def threshold(self, minval, maxval=255):
        cv2.threshold(self.img, minval, maxval, cv2.THRESH_BINARY, dst=self.img)
        
    def threshold_inverted(self, minval, maxval=255):
        cv2.threshold(self.img, minval, maxval, cv2.THRESH_BINARY_INV, dst=self.img)
        
    def threshold_otsu(self):
        cv2.threshold(self.img, 0, 0xff, cv2.THRESH_BINARY | cv2.THRESH_OTSU, dst=self.img)
        
