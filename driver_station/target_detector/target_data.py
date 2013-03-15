
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

kOptimumVerticalPosition = 0.7


# target location types
location = common.enum(TOP=0, 
                       LMIDDLE=3,   # left of top
                       RMIDDLE=4,   # right of top
                       MIDDLE=1,    # unknown
                       LOW=2)

class Target(object):
    
    __slots__ = ['x', 'y', 'w', 'h', 'cx', 'cy', 'polygon', 'location', 'ratio']
    
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
        return int(self.x + self.w/2.0), int(self.y + self.h/2.0)
    
    def intersects(self, x, y):
        return cv2.pointPolygonTest(self.polygon, (x, y), False) >= 0
        
    def get_measurements(self):
        
        # TODO: Fix these up 
        # TODO: Do these really belong here? Just don't want to calculate
        # them all the time for every potential target.. 
        
        # horizontal angle and vertical angle calculations from Youssef's code from 2012
        hangle = (iw / 2.0 - pCenterX) * self.kHorizontalFOVDeg / iw            
        vangle = ((ih * self.kOptimumVerticalPosition) - pCenterY) / (ih / self.kVerticalFOVDeg)

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
        
        theta = (centerOfImageY - pCenterY)/centerOfImageY * self.kVerticalFOVDeg/2.0 + self.cameraMountAngle
        distance = (tgt_center - self.cameraMountHeight) / math.tan(math.radians(theta))  
        
        
        return hangle, vangle, distance
        
    

class Targets(object):
    pass
    