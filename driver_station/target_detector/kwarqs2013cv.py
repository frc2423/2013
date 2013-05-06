#
#   This file is part of KwarqsDashboard.
#
#   KwarqsDashboard is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, version 3.
#
#   KwarqsDashboard is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with KwarqsDashboard.  If not, see <http://www.gnu.org/licenses/>.
#


import math
import sys

import cv2
import numpy as np

import target_data

from common import settings

# using python 2.7, get some python 3 builtins
from future_builtins import zip

import logging
logger = logging.getLogger(__name__)


class TargetDetector(object):
    '''
        Kwarqs 2013 Image Processing module, originally derived from Team 341's
        image processing code (written in Java), which appears to be originally 
        derived from a FRC SmartDashboard sample. 
    '''
    
    contourColor = (255,128, 0)
    missedColor  = (255,255,0)
    missedChildColor  = (0xd4, 255, 128)
    badRatioColor = (154,250,0)
    
    # each target type has a different color
    kTopColor     = (  0, 0, 255)   # red
    kMidColor     = (255, 0, 255)   # magenta
    kLowColor     = (255, 0,   0)   # blue
    
    #kLineType     = 8               # ugly lines, but faster
    kLineType     = cv2.CV_AA       # nicer anti aliased lines.. no noticeable slowdown
    
    # constants that need to be tuned
    kNearlyHorizontalSlope = math.tan(math.radians(20))
    kNearlyVerticalSlope = math.tan(math.radians(90-20))
    
    #kHorizontalFOVDeg = 47.0        # AXIS M1011 field of view
    kHorizontalFOVDeg = 43.5         # AXIS M1011 field of view from WPILib
    kVerticalFOVDeg = 36.13          # from http://photo.stackexchange.com/questions/21536/how-can-i-calculate-vertical-field-of-view-from-horizontal-field-of-view
    
    # the minimum percentage size a defect should be to be considered
    # a partially obscured target 
    kObscuredTargetDefectPct = 0.25
    
    # import needed target data, save some typing
    kTopInnerRatio = target_data.kTopInnerRatio
    kTopOuterRatio = target_data.kTopOuterRatio
    kMidInnerRatio = target_data.kMidInnerRatio
    kMidOuterRatio = target_data.kMidOuterRatio
    kLowInnerRatio = target_data.kLowInnerRatio
    kLowOuterRatio = target_data.kLowOuterRatio
    
    kTopTgtHCenter = target_data.kTopTgtHCenter
    kMidTgtHCenter = target_data.kMidTgtHCenter
    kLowTgtHCenter = target_data.kLowTgtHCenter
    
    kTop = target_data.location.TOP
    kMid = target_data.location.MIDDLE
    kMidL = target_data.location.LMIDDLE
    kMidR = target_data.location.RMIDDLE
    kLow = target_data.location.LOW
    kUnkL = target_data.location.UNKNOWNL
    kUnkR = target_data.location.UNKNOWNR
    
    kOptimumVerticalPosition = target_data.kOptimumVerticalPosition
    kOptimumHorizontalPosition = target_data.kOptimumHorizontalPosition
    
    kRatios = [kTopOuterRatio, kMidOuterRatio, kLowOuterRatio]
    
    kCompThreshHueP = 30
    kCompThreshHueN = 75
    kCompThreshSat = 188
    kCompThreshVal = 16
    
    kPitThreshHueP = 45
    kPitThreshHueN = 75
    kPitThreshSat = 200
    kPitThreshVal = 55
    
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
        self.show_bin_overlay = False
        self.show_contours = False
        self.show_missed = False
        self.show_badratio = False
        self.show_ratio_labels = False
        self.show_labels = True
        self.show_hangle = True
        self.show_targets = True
        
        # thresholds
        self.thresh_hue_p = settings.get('camera/thresh_hue_p', self.kCompThreshHueP)
        self.thresh_hue_n = settings.get('camera/thresh_hue_n', self.kCompThreshHueN)
        self.thresh_sat = settings.get('camera/thresh_sat', self.kCompThreshSat)
        self.thresh_val = settings.get('camera/thresh_val', self.kCompThreshVal)
    
    def processImage(self, img):
        
        # reinitialize any time the image size changes         
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
            
            # TODO: tune kMinWidth
            
            # Note: if you set k to an even number, the detected
            # contours are offset by some N pixels. Sometimes.
            
            if w <= 320:
                k = 1
                offset = (0,0)
                self.kHoleClosingIterations = 2 # originally 9
                
                self.kMinWidth = 2
                
                # drawing 
                self.kThickness = 1
                self.kTgtThickness = 1 
                
                # accuracy of polygon approximation
                self.kPolyAccuracy = 10.0
                
            elif w <= 480:
                k = 2
                offset = (1,1)
                self.kHoleClosingIterations = 9 # originally 9
                
                self.kMinWidth = 5
                
                # drawing
                self.kThickness = 1
                self.kTgtThickness = 2
                
                # accuracy of polygon approximation
                self.kPolyAccuracy = 15.0
                 
            else:
                k = 3
                offset = (1,1)
                self.kHoleClosingIterations = 6 # originally 9
                
                self.kMinWidth = 10
                
                # drawing
                self.kThickness = 1 
                self.kTgtThickness = 2
                
                # accuracy of polygon approximation
                self.kPolyAccuracy = 20.0
            
            self.morphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k,k), anchor=offset)
            
            logging.info("New image size: %sx%s, morph size set to %s, %s iterations", w,h,k, self.kHoleClosingIterations)
        
        # get this outside the loop
        ih, iw = self.size
        centerOfImageY = ih/2.0
        
        # convert to HSV
        cv2.cvtColor(img, cv2.cv.CV_BGR2HSV, self.hsv)
        cv2.split(self.hsv, [self.hue, self.sat, self.val])
        
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
        
        # Find contours, retrieve the hierarchy of contours so we can figure out 
        # which contours are the inner/outer rectangle
        contours, hierarchy = cv2.findContours(self.bin.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
        
        # overlay the binarized image on the displayed image, instead of a separate picture
        if self.show_bin_overlay:
            img[cv2.cvtColor(self.bin, cv2.COLOR_GRAY2BGR) != 0] = 255
        
        if self.show_contours:
            cv2.drawContours(img, contours, -1, (255,0,0), thickness=self.kThickness, lineType=self.kLineType)
        
        # stores the target data
        ctargets = [None]*len(contours)
        
        # Uncomment this to draw on a blank background
        #img = np.zeros(shape=img.shape, dtype=np.uint8)
        
        for hidx, contour, in enumerate(contours):
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # remove noise (maybe check max width too?)
            if w < self.kMinWidth:
                continue
            
            # detect defects.. 
            
            contour32 = contour.astype(np.float32)
            
            # get the convex hull
            hull_idx = cv2.convexHull(contour32, clockwise=True, returnPoints=False)
            hull_pts = np.take(contour32, hull_idx, 0).reshape(-1,1,2)
            
            # create a polygon from this thing
            p = cv2.approxPolyDP(hull_pts, self.kPolyAccuracy, False)
            
            if not cv2.isContourConvex(p) or not (len(p) == 4 or len(p) == 5):
                # discard this too
                if self.show_missed:
                    cv2.drawContours(img, [p.astype(np.int32)], -1, self.missedColor, thickness=self.kThickness, lineType=self.kLineType)
                continue
            
            # calculate the actual length of the sides, and determine the ratio
            # based on that. the original code used the bounding box, but that
            # fails when trying to discriminate rectangles from each other
            ((centerX, centerY), (rw, rh), rotation) = cv2.minAreaRect(p)

            # sometimes minAreaRect decides to rotate the rectangle too much.
            # detect that and fix it. 
            if (w > h and rh < rw) or (h > w and rw < rh):
                rh, rw = rw, rh  # swap
            
            ratio = float(rw)/rh
            
            # most things at this point will be a rectangle. Try to determine
            # if there are any partially obscured targets in the image.
            # -> Look for rectangles that have at least one large defect 
            #    along the edge of the image that is greater than 25% of the 
            #    width, and are at the edge of the image
            defects = cv2.convexityDefects(contour, hull_idx)
            
            if defects is not None:
                big_defect = rw * self.kObscuredTargetDefectPct
                
                for i in xrange(defects.shape[0]):
                    start_idx, end_idx, far_idx, depth = defects[i,0]
                    if (depth / 255.0) > big_defect:
                        
                        x1 = contour[start_idx, 0, 0]
                        x2 = contour[end_idx, 0, 0]
                        
                        # determine if its on the side of the image
                        # -> if so, this might be an obscured target
                        if x1 < 5 and x2 < 5: 
                            ratio = None
                            tgt = self.kUnkL
                            break
                        
                        elif iw - x1 < 5 and iw - x2 < 5:
                            ratio = None
                            tgt = self.kUnkR
                            break
            
            # TODO: get rid of magic constants
            
            if ratio is not None:
            
                if ratio >= self.kTopInnerRatio - 0.1 and ratio <= self.kTopOuterRatio + 0.03:
                    tgt = self.kTop
                    
                elif ratio >= self.kMidInnerRatio - 0.1 and ratio <= self.kMidOuterRatio + 0.2:
                    tgt = self.kMid
                    
                elif ratio >= self.kLowInnerRatio - 0.2 and ratio <= self.kLowOuterRatio + 0.4:
                    tgt = self.kLow
                    
                else:
                    # discard this object
                    
                    if self.show_badratio:
                        cv2.drawContours(img, [p.astype(np.int32)], -1, self.badRatioColor, thickness=self.kThickness, lineType=self.kLineType)
                    
                        if self.show_ratio_labels:
                            cv2.putText(img, '%.3f' % ratio, (x+5,y+5), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), bottomLeftOrigin=False)
                    
                    continue            
                    
            # We passed the first test...we fit a rectangle to the polygon
            # Now do some more tests
            
            # We expect to see a top line that is nearly horizontal, and two side lines that are nearly vertical
            numNearlyHorizontal = 0
            numNearlyVertical = 0
            
            for i in xrange(0,4):
                dy = p[i, 0, 1] - p[(i+1)%4, 0, 1]
                dx = p[i, 0, 0] - p[(i+1)%4, 0, 0] 
                slope = sys.float_info.max
                
                if dx != 0:
                    slope = abs(float(dy)/dx)
                
                if slope < self.kNearlyHorizontalSlope:
                    numNearlyHorizontal += 1
                elif slope > self.kNearlyVerticalSlope:
                    numNearlyVertical += 1
                    
            # discard anything that isn't squarish
            if numNearlyHorizontal == 0 or numNearlyVertical != 2:
                if self.show_missed:
                    cv2.drawContours(img, [p.astype(np.int32)], -1, self.missedColor, thickness=self.kThickness, lineType=self.kLineType)
                continue
            
            # store for hierarchical analysis 
            ctargets[hidx] = target_data.Target(x, y, w, h, p.astype(np.int32), tgt, ratio)               
                    
        #
        # ok, now that we have our target data gathered, prune it using the
        # hierarchy created by findContours
        #
        
        # hierarchy row elements: next, prev, child, parent
        all_targets = []

        for hidx, target in enumerate(ctargets):
            
            if target is None:
                continue
            
            # if there's no parent, just keep the target
            parent_idx = hierarchy[0,hidx,3]
            if parent_idx == -1:
                all_targets.append(target)
                continue
            
            parent = ctargets[parent_idx] 
            
            # if there is a target, and the parent isn't a target, keep it
            if parent is None:
                all_targets.append(target)
                continue
            
            # if the type is UNKNOWN, and it has a parent that is a target, get rid of it
            if target.location == self.kUnkL or target.location == self.kUnkR:
                pass
            
            else:
                # if it is, and they disagree on type, whichever difference is 
                # closer... change the parent to that one
                if parent.location != target.location:
                    # TODO?
                    pass
            
            # the child will be discarded
            if self.show_missed:
                cv2.drawContours(img, [target.polygon], -1, self.missedChildColor, thickness=self.kThickness, lineType=self.kLineType)
                
                if self.show_ratio_labels:
                    cv2.putText(img, '%.3f' % target.ratio, (target.x,target.y), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), bottomLeftOrigin=False)
            
        #
        # categorize the targets according to position
        #
        
        lows = []
        mids = []
        tops = []
        unks = []
        
        #
        # split the targets into groups
        #
        
        for i, target in enumerate(all_targets):
            if target is None:
                continue
            
            if target.location == self.kTop:
                tops.append(target)
              
            elif target.location == self.kMid:
                mids.append(target)
             
            elif target.location == self.kLow:
                lows.append(target)
            
            else:
                unks.append(target)

        #
        # determine what the unknown targets are, based on their relative
        # position to other targets
        #
        
        if len(unks) != 0:
            if len(tops) != 0:
                
                # sort the tops by the highest target
                # -> lowest numeric value is the highest!
                tops.sort(key=lambda tgt: tgt.cy)
                
                for target in unks:
                    if target.cy > tops[0].cy + tops[0].h * 0.5:
                        target.location = self.kMid
                        mids.append(target)
                
            elif len(mids) != 0:
                mids.sort(key=lambda tgt: tgt.cy)
                
                for target in unks:
                    if target.cy < mids[0].cy - mids[0].h * 0.1:
                        target.location = self.kTop
                        tops.append(target)
                                                    
                    elif target.cy > mids[0].cy + mids[0].h:
                        target.location = self.kLow
                        lows.append(target)
                        
                    else:
                        target.location = self.kMid
                        mids.append(target)
        
        # determine the left and right middle targets if possible
        # -> There's probably a better way to do this.. 
        
        # since the leftmost is first, the left most target is probably 
        # the left target.. 
        next = target_data.location.LMIDDLE
        label = 'L-MID'
        
        if len(tops) != 0:
            
            # if there is more than one top, then assume the highest one is 
            # the true top.. because there can only be one.  
            
            if len(tops) > 1:
                
                # sort the tops by the highest target
                # -> lowest numeric value is the highest!
                tops.sort(key=lambda tgt: tgt.cy)
                
                mids += tops[1:]
                tops = [tops[0]]
            
            top = tops[0]
            
            # sort the middles by their left most edge    
            mids.sort(key=lambda tgt: tgt.x)
                    
            for target in mids:
                # the left most target is probably the left target.. 
                if target.x < top.x: 
                    target.location = next
                    next = target_data.location.MIDDLE
                else:
                    target.location = target_data.location.RMIDDLE
        else:
            
            # if there are no top targets identified, we cannot reliably
            # determine where the other targets are. We probably don't
            # care where they are either, honestly.
            
            pass
                 
                    
        all_targets = lows + mids + tops
        
        #
        # Ok, now that mess is done, actually draw the things and calculate measurements
        #
        
        def _draw_target(target, label):
            if not self.show_targets:
                return 
                
            components = []
            cv2.drawContours(img, [target.polygon], -1, target.color, thickness=self.kTgtThickness, lineType=self.kLineType)
            
            cv2.circle(img, (target.cx, target.cy), 3, target.color)
            
            if self.show_labels:
                components.append(label)
                
            if self.show_hangle:
                components.append('%.1f' % target.hangle)
                
            if self.show_ratio_labels:
                components.append('R%.3f' % target.ratio if target.ratio is not None else 'None')
            
            if len(components) != 0:
                cv2.putText(img, ' '.join(components), (target.x,target.y), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), bottomLeftOrigin=False)
        
        
        for i, target in enumerate(all_targets):
                        
            # calculate the targeting information and draw them
            
            if target.location == self.kTop:
                target.color = self.kTopColor
                self._set_measurements(iw, ih, target, self.kTopTgtHCenter, centerOfImageY)
                _draw_target(target, 'TOP')
                
            elif target.location == self.kMid:
                target.color = self.kMidColor
                self._set_measurements(iw, ih, target, self.kMidTgtHCenter, centerOfImageY)
                _draw_target(target, 'MID')
                
            elif target.location == self.kMidL:
                target.color = self.kMidColor
                self._set_measurements(iw, ih, target, self.kMidTgtHCenter, centerOfImageY)
                _draw_target(target, 'LMID')
                
            elif target.location == self.kMidR:
                target.color = self.kMidColor
                self._set_measurements(iw, ih, target, self.kMidTgtHCenter, centerOfImageY)
                _draw_target(target, 'RMID')
                
            elif target.location == self.kLow:
                target.color = self.kLowColor
                self._set_measurements(iw, ih, target, self.kLowTgtHCenter, centerOfImageY)
                _draw_target(target, 'LOW')
        
                    
        # sort the low targets
        lows.sort(key=lambda tgt: tgt.cy)
            
        cat_tgts = {'top': tops,
                    'mid': mids,
                    'low': lows}
            
        return img, all_targets, cat_tgts
    
    
    def _set_measurements(self, iw, ih, target, tgt_center, centerOfImageY):
        
        # horizontal angle and vertical angle calculations from Youssef's code from 2012
        target.hangle = (iw * self.kOptimumHorizontalPosition - target.cx) * self.kHorizontalFOVDeg / iw            
        target.vangle = ((ih * self.kOptimumVerticalPosition) - target.cy) / (ih / self.kVerticalFOVDeg)

        # Distance calculations from Stephen

        # Distance to the goal is a function of the height of the goal      
        # (kTopTgtHCenter) and the angle between the camera and the goal    
        # (theta). The formula is just d = height / tan(theta)              

        # First, want to find out angle between camera and center of goal   
        # If the center of the goal is in the middle of the image, then     
        # theta will be 0 degrees. If the center of the goal is at          
        # the top of the image, then theta will be kVerticalFOVDeg/2        
        # Similarly, if the center of the goal is at the bottom of the     
        # image, then theta will be -kVerticalFOVDeg/2
        
        # We also have to take into account the angle the camera is mounted
        # We can apply linear interpolation to figure all points in between
        
        theta = (centerOfImageY - target.cy)/centerOfImageY * self.kVerticalFOVDeg/2.0 + self.cameraMountAngle
        target.distance = (tgt_center - self.cameraMountHeight) / math.tan(math.radians(theta))  
        
        # TODO: The distance doesn't actually work yet. We should fix that sometime...  

