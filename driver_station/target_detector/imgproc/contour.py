
import cv2

class CvContour(object):
    # TODO: is this useful?
    
    __slots__ = ['contour', 'x', 'y', 'w', 'h', 'area']
    
    def __init__(self, contour):
        x,y,w,h = cv2.boundingRect(contour)
        
        self.contour = contour
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
        #self.area = cv2.contourArea(contour)

    def approxPoly(self, accuracy):
        poly = cv2.approxPolyDP(self.contour, accuracy, True)
        return CvContour(poly)