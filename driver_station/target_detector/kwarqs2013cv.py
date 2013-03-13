
import math
import sys

import cv2
import numpy as np

import target_data

from common import settings

import logging
logger = logging.getLogger(__name__)


class TargetDetector(object):
    
    contourColor = (255, 0, 0)
    missedColor  = (255,255,0)
    maybeColor   = (0, 0, 255)
    
    # constants that need to be tuned
    kNearlyHorizontalSlope = math.tan(math.radians(20))
    kNearlyVerticalSlope = math.tan(math.radians(90-20))
    kMinWidth = 20
    kMaxWidth = 200
    kRangeOffset = 0.0
    
    # accuracy of polygon approximation
    # -> TODO: determine what this actually means, seems like
    #          it should be lower at lower resolutions
    kPolyAccuracy = 10.0

    kShooterOffsetDeg = 0.0
    #kHorizontalFOVDeg = 47.0        # AXIS M1011 field of view
    kHorizontalFOVDeg = 43.5         # AXIS M1011 field of view from WPILib
    kVerticalFOVDeg = 36.13         # from http://photo.stackexchange.com/questions/21536/how-can-i-calculate-vertical-field-of-view-from-horizontal-field-of-view
    AXIS_CAMERA_VIEW_ANGLE = math.pi * 38.33 / 180.0
    
    kCameraHeightIn = 33.0      # 18 to 26 inches
    kCameraPitchDeg = 11.5
    
    # import needed target data
    kTopOuterRatio = target_data.kTopOuterRatio
    kMidOuterRatio = target_data.kMidOuterRatio
    kLowOuterRatio = target_data.kLowOuterRatio
    
    kTop = target_data.location.TOP
    kMid = target_data.location.MIDDLE
    kLow = target_data.location.LOW
    
    def __init__(self):
        self.size = None
        
        # TODO: fix the angle and such up with real values
        # TODO: Update these on the fly from network tables
        self.cameraMountAngle = 11.5   # degrees
        self.cameraMountHeight = 12.0  # inches
        
        # debug settings        
        self.show_hue = False
        self.show_sat = False
        self.show_val = False
        self.show_bin = False
        self.show_contours = False
        self.show_missed = False
        self.show_targets = True
        
        # thresholds
        self.thresh_hue_p = settings.get('camera/thresh_hue_p', 60-15)
        self.thresh_hue_n = settings.get('camera/thresh_hue_n', 60+15)
        self.thresh_sat = settings.get('camera/thresh_sat', 200)
        self.thresh_val = settings.get('camera/thresh_val', 55)
    
    def processImage(self, img):
        
        # reinitialize anytime the image size changes         
        if self.size is None or self.size[0] != img.shape[0] or self.size[1] != img.shape[1]:
            h, w = img.shape[:2]
            self.size = (h, w)
            
            # these are preallocated so we aren't allocating all the time
            self.bin = np.empty((h, w, 1), dtype=np.uint8)
            self.hsv = np.empty((h, w, 3), dtype=np.uint8)
            self.hue = np.empty((h, w, 1), dtype=np.uint8)
            self.sat = np.empty((h, w, 1), dtype=np.uint8)
            self.val = np.empty((h, w, 1), dtype=np.uint8)
            
            # these settings should be adjusted according to the image size
            # and noise characteristics
            
            # TODO: What's the optimal setting for this? For smaller images, we
            # cannot morph as much, or the features blend into each other. 
            
            # Note: if you set k to an even number, the detected
            # contours are offset by some N pixels
            
            if w <= 320:
                k = 1
                offset = (0,0)
                self.kHoleClosingIterations = 2 # originally 9
                
            elif w <= 480:
                k = 2
                offset = (1,1)
                self.kHoleClosingIterations = 9 # originally 9
                
            else:
                k = 3
                offset = (0,0)
                self.kHoleClosingIterations = 9 # originally 9
                
            self.morphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k,k), anchor=offset)
            
            logging.info("New image size: %sx%s, morph size set to %s, %s iterations", w,h,k, self.kHoleClosingIterations)
        
        # get this outside the loop
        ih, iw = self.size
        centerOfImageY = ih/2.0
        
        # convert to HSV
        cv2.cvtColor(img, cv2.cv.CV_BGR2HSV, self.hsv)
        cv2.split(self.hsv, [self.hue, self.sat, self.val])
        
        # uncommment this to draw on zeroed image
        #img = np.zeros(img.shape, dtype=np.uint8)
        
        # Threshold each component separately
        # Hue
        # NOTE: Red is at the end of the color space, so you need to OR together
        # a thresh and inverted thresh in order to get points that are red
        cv2.threshold(self.hue, self.thresh_hue_p, 255, type=cv2.THRESH_BINARY, dst=self.bin)
        cv2.threshold(self.hue, self.thresh_hue_n, 255, type=cv2.THRESH_BINARY_INV, dst=self.hue)
        
        # Saturation
        cv2.threshold(self.sat, self.thresh_sat, 255, type=cv2.THRESH_BINARY, dst=self.sat)
        
        if self.show_sat:
            cv2.imshow('sat', self.sat)
        
        # Value
        cv2.threshold(self.val, self.thresh_val, 255, type=cv2.THRESH_BINARY, dst=self.val)
        
        if self.show_val:
            cv2.imshow('val', self.val)
        
        # Combine the results to obtain our binary image which should for the most
        # part only contain pixels that we care about
        cv2.bitwise_and(self.hue, self.bin, self.bin)
        
        if self.show_hue:
            cv2.imshow('hue', self.bin)
        
        cv2.bitwise_and(self.bin, self.sat, self.bin)
        cv2.bitwise_and(self.bin, self.val, self.bin)

        # Fill in any gaps using binary morphology
        cv2.morphologyEx(self.bin, cv2.MORPH_CLOSE, self.morphKernel, dst=self.bin, iterations=self.kHoleClosingIterations)
        
        if self.show_bin:
            cv2.imshow('bin', self.bin)
        
        targets = []
        
        # TODO: Find all contours, but use the hierarchy to find contours that
        #       exist inside of another contour?

        
        # Find contours
        contours, hierarchy = cv2.findContours(self.bin.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
        contours = [cv2.convexHull(c.astype(np.float32), clockwise=True, returnPoints=True) for c in contours]
        
        # TODO: if we use cv2.RETR_TREE, then we can iterate through contours
        # and find contours that are inside other contours. This could help
        # establish better rectangles
        
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            ratio = float(h)/w
            
            #if ratio < 1.0 and ratio > 0.5 and w > self.kMinWidth and w < self.kMaxWidth:
            # if w > self.kMinWidth
            #    continue
            
            if self.show_contours:
                cv2.drawContours(img, [c.astype(np.int32)], -1, (255,0,0))
                
            #continue
            
            if abs(ratio - self.kTopOuterRatio) < 0.25:
                p = cv2.approxPolyDP(c, self.kPolyAccuracy, False)
                tgt = target_data.location.TOP
                
            elif abs(ratio - self.kMidOuterRatio) < 0.25:
                p = cv2.approxPolyDP(c, self.kPolyAccuracy, False)
                tgt = target_data.location.MIDDLE
                
            elif abs(ratio - self.kLowOuterRatio) < 0.25:
                p = cv2.approxPolyDP(c, self.kPolyAccuracy, False)
                tgt = target_data.location.LOW
                
            else:
                # discard this object
                continue
            
            #cv2.drawContours(img, [p.astype(np.int32)], -1, (255,255,0))
            
            if not cv2.isContourConvex(p) or not (len(p) == 4 or len(p) == 5):
                # discard this too
                if self.show_missed:
                    cv2.drawContours(img, [p.astype(np.int32)], -1, self.missedColor, thickness=1)
                continue
                
                
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
                    
            # discard anything that isn't squarish
            if numNearlyHorizontal == 0 or numNearlyVertical != 2:
                continue
            
            targets.append(target_data.Target(x, y, w, h, p, tgt))          
            
            if self.show_targets:     
                cv2.drawContours(img, [p.astype(np.int32)], -1, self.maybeColor, thickness=2)
            
        
        # does it make more sense to do this part in the UI thread?
            
        # categorize the targets according to position
        lows = []
        mids = []
        tops = []
        
        for tgt in targets:
            if tgt.location == self.kTop:
                tops.append(tgt)
            elif tgt.location == self.kMid:
                mids.append(tgt)
            elif tgt.location == self.kLow:
                lows.append(tgt)
        
        # determine the left and right targets if possible
        if len(tops) != 0:

            # -> sort by their left most edge
            #    does it make sense to sort by their center instead?
        
            mids.sort(key=lambda tgt: tgt.x)
                    
            # sort the tops by the highest target
            tops.sort(key=lambda tgt: tgt.y, reverse=True)
            top = tops[0]
            
            next = target_data.location.LMIDDLE
                    
            for tgt in mids:
                if tgt.x < top.x:
                    tgt.location = next
                    next = target_data.location.RMIDDLE 
                else:
                    tgt.location = target_data.location.RMIDDLE   
                    
        # sort the low targets
        lows.sort(key=lambda tgt: tgt.y, reverse=True)         
            
        cat_tgts = {'top': tops,
                    'mid': mids,
                    'low': lows}
            
        return img, targets, cat_tgts
    
