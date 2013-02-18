
import math
import sys

import cv2
import numpy as np


class TargetDetector(object):
    
    targetColor = (0, 255, 0)
    missedColor = (255,255,0)
    
    # constants that need to be tuned
    kNearlyHorizontalSlope = math.tan(math.radians(20))
    kNearlyVerticalSlope = math.tan(math.radians(90-20))
    kMinWidth = 20
    kMaxWidth = 200
    kRangeOffset = 0.0
    kHoleClosingIterations = 9

    kShooterOffsetDeg = -1.55
    kHorizontalFOVDeg = 47.0

    kVerticalFOVDeg = 480.0/640.0*kHorizontalFOVDeg
    kCameraHeightIn = 54.0
    kCameraPitchDeg = 21.0
    kTopTargetHeightIn = 98.0 + 2.0 + 9.0 # 98 to rim, +2 to bottom of target, +9 to center of target
    
    kRatioLow = 32.0/37.0
    kRatioMid = 29.0/62.0
    kRatioHigh = 20.0/62.0
    
    def __init__(self):
        self.morphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3), anchor=(1,1))
        self.size = None
        print self.kRatioLow, self.kRatioMid, self.kRatioHigh
    
    def processImage(self, img):
        
        # Get the current heading of the robot first
        heading = 0
        
        if self.size is None or self.size[0] != img.shape[0] or self.size[1] != img.shape[1]:
            h, w = img.shape[:2]
            self.size = (h, w)
            self.bin = np.empty((h, w, 1), dtype=np.uint8)
            self.hsv = np.empty((h, w, 3), dtype=np.uint8)
            self.hue = np.empty((h, w, 1), dtype=np.uint8)
            self.sat = np.empty((h, w, 1), dtype=np.uint8)
            self.val = np.empty((h, w, 1), dtype=np.uint8)
            
            horizontalOffsetPixels =  int(self.kShooterOffsetDeg*(w/self.kHorizontalFOVDeg))
            self.linePt1 = (w/2 + horizontalOffsetPixels, h-1)
            self.linePt2 = (w/2 + horizontalOffsetPixels,0)
            
            self.kVerticalFOVDeg = (float(h)/w) * self.kHorizontalFOVDeg
        
        # convert to HSV
        cv2.cvtColor(img, cv2.cv.CV_BGR2HSV, self.hsv)
        cv2.split(self.hsv, [self.hue, self.sat, self.val])
        
        # uncommment this to draw on zeroed image
        #img = np.zeros(img.shape, dtype=np.uint8)
        
        # Threshold each component separately
        # Hue
        # NOTE: Red is at the end of the color space, so you need to OR together
        # a thresh and inverted thresh in order to get points that are red
        cv2.threshold(self.hue, 60-15, 255, type=cv2.THRESH_BINARY, dst=self.bin)
        cv2.threshold(self.hue, 60+15, 255, type=cv2.THRESH_BINARY_INV, dst=self.hue)
        
        # Saturation
        cv2.threshold(self.sat, 200, 255, type=cv2.THRESH_BINARY, dst=self.sat)
        
        # Value
        cv2.threshold(self.val, 55, 255, type=cv2.THRESH_BINARY, dst=self.val)
        
        # Combine the results to obtain our binary image which should for the most
        # part only contain pixels that we care about
        cv2.bitwise_and(self.hue, self.bin, self.bin)
        cv2.bitwise_and(self.bin, self.sat, self.bin)
        cv2.bitwise_and(self.bin, self.val, self.bin)
        
        # Uncommment this to show the thresholded image
        #cv2.imshow('bin', self.bin)

        # Fill in any gaps using binary morphology
        cv2.morphologyEx(self.bin, cv2.MORPH_CLOSE, self.morphKernel, dst=self.bin, iterations=self.kHoleClosingIterations)
        
        #cv2.imshow('morph', self.bin)
        
        # Find contours
        contours = self.findConvexContours(self.bin)
        polygons = []
        
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            ratio = float(h)/w
            
            #if ratio < 1.0 and ratio > 0.5 and w > self.kMinWidth and w < self.kMaxWidth:
            # if w > self.kMinWidth
            #    continue
            
            print 'ratio', ratio, abs(ratio - self.kRatioHigh), abs(ratio - self.kRatioMid), abs(ratio - self.kRatioLow)
            
            if abs(ratio - self.kRatioHigh) < 0.25:
                p = cv2.approxPolyDP(c, 20, False)
                polygons.append((p, x, y, w, h, 'hi'))
                
            elif abs(ratio - self.kRatioMid) < 0.25:
                p = cv2.approxPolyDP(c, 20, False)
                polygons.append((p, x, y, w, h, 'mid'))
                
            elif abs(ratio - self.kRatioLow) < 0.25:
                p = cv2.approxPolyDP(c, 20, False)
                polygons.append((p, x, y, w, h, 'lo'))
                
                
        square = None
        highest = sys.maxint 
        
        for p, x, y, w, h, spot in polygons:
            if cv2.isContourConvex(p) and len(p) == 4:
                
                # We passed the first test...we fit a rectangle to the polygon
                # Now do some more tests
                
                # We expect to see a top line that is nearly horizontal, and two side lines that are nearly vertical
                numNearlyHorizontal = 0
                numNearlyVertical = 0
                
                for i in xrange(0,4):
                    dy = p[i, 0, 0] - p[(i+1)%4, 0, 0]
                    dx = p[i, 0, 1] - p[(i+1)%4, 0, 1] 
                    slope = sys.float_info.max
                    
                    if dx != 0:
                        slope = abs(dy/dx)
                
                    if slope < self.kNearlyHorizontalSlope:
                        numNearlyHorizontal += 1
                    elif slope > self.kNearlyVerticalSlope:
                        numNearlyVertical += 1
                        
                if numNearlyHorizontal >= 1 and numNearlyVertical == 2:
                    
                    pCenterX = int(x + w/2.0)
                    pCenterY = int(y + h/2.0)
                    
                    # drawPoint
                    cv2.circle(img, (pCenterX, pCenterY), 5, self.targetColor) 
                    
                    if pCenterY < highest:  # because coord system is funny
                        square = (p, x, y, w, h, spot)
                        highest = pCenterY
            
            else:
                cv2.drawContours(img, [p.astype(np.int32)], -1, self.missedColor, thickness=1)
            
        if square is not None:
            square, x, y, w, h, spot = square
            
            print 'Decided on %s' % spot
            
            x = x + w/2
            x = 2 * (x/w)-1
            
            y = y + (h/2)
            y = -((2 * (y/h)) - 1)
            
            azimuth = (x*self.kHorizontalFOVDeg/2.0 + heading - self.kShooterOffsetDeg) % 360.0
            range = (self.kTopTargetHeightIn - self.kCameraHeightIn)/math.tan((y*self.kVerticalFOVDeg/2.0 + self.kCameraPitchDeg) * math.pi/180.0)
            
            
            print 'range, a', range, azimuth
            # get rpms from this data
            
            # send data to someone using pynetworktables
            
            # draw the square on the target and show it
            cv2.drawContours(img, [square.astype(np.int32)], -1, self.targetColor, thickness=7)
            
        return img
        
        
    def boundAngle0to360Degrees(self, angle):
        # Naive algorithm
        while (angle >= 360.0):
            angle -= 360.0
            
        while (angle < 0.0):
            angle += 360.0
            
        return angle
    
    def findConvexContours(self, img): 
        img = img.copy()
        
        contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
        return [cv2.convexHull(c.astype(np.float32), clockwise=True, returnPoints=True) for c in contours]
    
