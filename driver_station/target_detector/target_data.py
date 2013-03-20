
import common
import cv2

# target data in inches
kTapeWidth      = 4.0

kTopHeight      = 12.0          # inner height
kTopWidth       = 54.0          # inner width
kTopEdgeHeight  = 104.125       # height from ground to bottom edge (not including tape)
kTopTgtHCenter  = kTopEdgeHeight + kTopHeight/2.0   # height from ground to center of target

kTopInnerRatio  = kTopHeight/kTopWidth                                    # 0.222222222222 
kTopOuterRatio  = (kTopHeight + kTapeWidth*2)/(kTopWidth + kTapeWidth*2)  # 0.322580645161

kMidHeight      = 21.0
kMidWidth       = 54.0
kMidEdgeHeight  = 88.625
kMidTgtHCenter  = kMidEdgeHeight + kMidHeight/2.0

kMidInnerRatio  = kMidHeight/kMidWidth                                    # 0.388888888889 
kMidOuterRatio  = (kMidHeight + kTapeWidth*2)/(kMidWidth + kTapeWidth*2)  # 0.467741935484

kLowHeight      = 24.0
kLowWidth       = 29.0
kLowEdgeHeight  = 19.0
kLowTgtHCenter  = kLowEdgeHeight + kLowHeight/2.0

kLowInnerRatio  = kLowHeight/kLowWidth                                    # 0.827586206897 
kLowOuterRatio  = (kLowHeight + kTapeWidth*2)/(kLowWidth + kTapeWidth*2)  # 0.864864864865

kOptimumVerticalPosition = 0.7      # percent from top
kOptimumHorizontalPosition = 0.55    # percent from left


# target location types
location = common.enum(TOP=0, 
                       LMIDDLE=3,   # left of top
                       RMIDDLE=4,   # right of top
                       MIDDLE=1,    # unknown middle
                       LOW=2,
                       UNKNOWNL=5,
                       UNKNOWNR=6)

class Target(object):
    
    def __init__(self, x, y, w, h, polygon, location, ratio):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cx = int(x + w/2.0)    # center x
        self.cy = int(y + h/2.0)    # center y
        self.polygon = polygon
        self.location = location
        self.ratio = ratio
        
    def get_center(self):
        return self.cx, self.cy
    
    def intersects(self, x, y):
        return cv2.pointPolygonTest(self.polygon, (x, y), False) >= 0
    
    def h_ok(self):
        '''Horizontal angle on target'''
        return abs(self.hangle) <= 2.0
    
    def v_ok(self):
        '''Vertical angle on target'''
        return abs(self.vangle) <= 2.0
