
import math
import sys

import cv2
import numpy as np


class TargetDetector(object):
    
    targetColor = (0, 255, 0)
    missedColor = (255,255,0)
    maybeColor =  (0, 0, 255)
    
    # constants that need to be tuned
    kNearlyHorizontalSlope = math.tan(math.radians(20))
    kNearlyVerticalSlope = math.tan(math.radians(90-20))
    kMinWidth = 20
    kMaxWidth = 200
    kRangeOffset = 0.0
    kHoleClosingIterations = 9

    kShooterOffsetDeg = 0.0
    #kHorizontalFOVDeg = 47.0        # AXIS M1011 field of view
    kHorizontalFOVDeg = 43.5         # AXIS M1011 field of view from WPILib
    kVerticalFOVDeg = 36.13         # from http://photo.stackexchange.com/questions/21536/how-can-i-calculate-vertical-field-of-view-from-horizontal-field-of-view
    AXIS_CAMERA_VIEW_ANGLE = math.pi * 38.33 / 180.0
    
    kCameraHeightIn = 33.0      # 18 to 26 inches
    kCameraPitchDeg = 11.5
    
    # target data in inches
    kTapeWidth = 4.0
    
    kTopHeight      = 12.0          # inner height
    kTopWidth       = 54.0          # inner width
    kTopEdgeHeight  = 104.125       # height from ground to bottom edge (not including tape)
    kTopTgtHCenter  = kTopEdgeHeight + kTopHeight/2.0   # height from ground to center of target
    
    kTopInnerRatio  = kTopHeight/kTopWidth
    kTopOuterRatio  = (kTopHeight + kTapeWidth*2)/(kTopWidth + kTapeWidth*2)
    
    kMidHeight      = 21.0
    kMidWidth       = 54.0
    kMidEdgeHeight  = 88.625
    kMidTgtHCenter  = kMidEdgeHeight + kMidHeight/2.0
    
    kMidInnerRatio  = kMidHeight/kMidWidth
    kMidOuterRatio  = (kMidHeight + kTapeWidth*2)/(kMidWidth + kTapeWidth*2)
    
    kLowHeight      = 24.0
    kLowWidth       = 29.0
    kLowEdgeHeight  = 19.0
    kLowTgtHCenter  = kLowEdgeHeight + kLowHeight/2.0
    
    kLowInnerRatio  = kLowHeight/kLowWidth
    kLowOuterRatio  = (kLowHeight + kTapeWidth*2)/(kLowWidth + kTapeWidth*2)
    
    kOptimumVerticalPosition = 0.4
    
    def __init__(self, table):
        self.morphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3), anchor=(1,1))
        self.size = None
        self.table = table
    
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
            
            #self.kVerticalFOVDeg = (float(h)/w) * self.kHorizontalFOVDeg
        
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
        #cv2.threshold(self.sat, 200, 255, type=cv2.THRESH_BINARY, dst=self.sat)
        cv2.threshold(self.sat, 100, 255, type=cv2.THRESH_BINARY, dst=self.sat)
        
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
            
            # uncomment to see all original contours
            #cv2.drawContours(img, [c.astype(np.int32)], -1, (0,0,255))
            
            if abs(ratio - self.kTopOuterRatio) < 0.25:
                p = cv2.approxPolyDP(c, 20, False)
                polygons.append((p, x, y, w, h, self.kTopTgtHCenter))
                
            elif abs(ratio - self.kMidOuterRatio) < 0.25:
                p = cv2.approxPolyDP(c, 20, False)
                polygons.append((p, x, y, w, h, self.kMidTgtHCenter))
                
            elif abs(ratio - self.kLowOuterRatio) < 0.25:
                p = cv2.approxPolyDP(c, 20, False)
                polygons.append((p, x, y, w, h, self.kLowTgtHCenter))
                
                
        square = None
        highest = sys.maxint 
        
        for p, x, y, w, h, tgt_center in polygons:
            if cv2.isContourConvex(p) and (len(p) == 4 or len(p) == 5):
                
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
                        slope = abs(float(dy)/dx)
                
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
                        square = (p, x, y, w, h, tgt_center)
                        highest = pCenterY
            
                cv2.drawContours(img, [p.astype(np.int32)], -1, self.maybeColor, thickness=1)
            else:
                cv2.drawContours(img, [p.astype(np.int32)], -1, self.missedColor, thickness=1)
            
        if square is not None:
            square, x, y, w, h, tgt_center = square
            ih, iw = self.size
            
            bCenterX = x + w/2.0
            bCenterY = y + h/2.0
            
            # youssef's calcs: angle is correct
            hangle = (iw / 2.0 - bCenterX) * self.kHorizontalFOVDeg / iw
            
            vangle = -((ih * self.kOptimumVerticalPosition) - h) / (ih / self.kVerticalFOVDeg)
            
            distance = (54.0 * iw) / (2.0 * x * math.tan(math.radians(self.kHorizontalFOVDeg)/2.0))
            
            #print self.kVerticalFOVDeg
            #distance = (12.0 * ih) / (2.0 * h * math.tan(self.kVerticalFOVDeg/2.0))
            
            # from WPILib... this actually isn't that terrible.. 
            #distance = (iw * 12.0 / (h * 12.0 * 2.0 * math.tan(math.radians(self.kHorizontalFOVDeg)))) 
            
            # sugg
            #distanceToTarget = (targetHeight-cameraHeight)/tan(cameraAngle+relativeTargetAngle)
            #double range = (kTopTargetHeightIn-kCameraHeightIn)/Math.tan((y*kVerticalFOVDeg/2.0 + kCameraPitchDeg)*Math.PI/180.0);
            #distance = = (self.kTopTgtHCenter - self.kCameraHeightIn)/(math.tan(y*self.kVerticalFOVDeg/2.0 + 11.5))
            
            # 
            #distance = ()
            
            print 'hAngle', hangle, 'distance', distance
            
            
            # daisy calcs
            x = x + w/2.0
            x = 2.0 * (x/w)-1
            
            y = y + (h/2.0)
            y = -((2.0 * (y/h)) - 1)
            
            #azimuth = (x*self.kHorizontalFOVDeg/2.0 + 90 - self.kShooterOffsetDeg) % 360.0
            range = (tgt_center - self.kCameraHeightIn)/math.tan(math.radians(y*self.kVerticalFOVDeg/2.0 + self.kCameraPitchDeg))
            #print 'range', range, tgt_center
            #print 'off, range, a', range, azimuth
            # get rpms from this data
            
            # send data to someone using pynetworktables
            
            
            
            
            # TODO: needs to be atomic
            if self.table is not None:
                self.table.PutNumber(u'Target HAngle', hangle)
                self.table.PutNumber(u'Target VAngle', vangle)
                self.table.PutNumber(u'Target Distance', distance)
                self.table.PutBoolean(u'Target Found', True)
            
            # draw the square on the target and show it
            cv2.drawContours(img, [square.astype(np.int32)], -1, self.targetColor, thickness=7)
            
        elif self.table is not None:
            self.table.PutBoolean(u'Target Found', False)
            
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
    
