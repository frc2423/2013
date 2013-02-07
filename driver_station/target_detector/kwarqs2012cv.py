
import math

import cv2
import numpy as np

from imgproc import CvImg, colorspace

class Kwarqs2012Cv(object):
    '''
        Image processing code developed for the Kwarqs in 2012
    '''

    AXIS_CAMERA_VIEW_ANGLE = math.pi * 38.33 / 180.0

    candidateColor = (255, 0, 0)
    missedColor = (255,255,0)
    targetColor = (0, 0, 255)

    def __init__(self):
        pass

    def daisy_threshold(self, cvimg):
        '''Thresholding technique from DaisyCv'''
        
        hsv = cvimg.clone()
        
        hsv.set_colorspace(colorspace.HSV)
        h, s, v = hsv.split()
        
        bin = h.clone()
        bin.threshold(60-15)
        h.threshold_inverted(60+15)
        
        s.threshold(200)
        v.threshold(55)
        
        bin.bitwise_and(h)
        bin.bitwise_and(s)
        bin.bitwise_and(v)
        
        return bin

    def processImage(self, img):        
        cvimg = CvImg(img, colorspace.BGR)
        
        # original code:
        # -> this works absolutely terribly on the test images
        #b, g, r = cvimg.split()
        #
        #b.threshold(0)
        #g.threshold(203)
        #r.threshold_inverted(170)
        #
        #final = b.bitwise_and(r).bitwise_and(g)
        
        # from DaisyCV:
        final = self.daisy_threshold(cvimg)
       
        final.dilate(6)
        
        # Uncomment this to draw on a blank background
        cvimg = cvimg.clone_zeroed()
        
        contours = final.find_contours()
        polygons = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            ratio = float(h) / w
            if ratio < 2.0 and ratio > 0.6:
                polygon = cv2.approxPolyDP(contour, 45, False)
                polygons.append((polygon, x, y, w, h))
        
        possiblePolygons = []
        for p, x, y, w, h in polygons:
            if cv2.isContourConvex(p) and len(p) == 4:
                possiblePolygons.append((p, x, y, w, h))
            else:
                cvimg.draw_contour(p, self.missedColor)
        
        insidePolygons = []
        for p in possiblePolygons:
            pp, px, py, pw, ph = p
            for q in possiblePolygons:
                qq, qx, qy, qw, qh = q
                if pp is qq:
                    continue
                
                pCenterX = px + pw / 2.0
                qCenterX = qx + qw / 2.0
                pCenterY = py + ph / 2.0
                qCenterY = qy + qh / 2.0
                
                dist_between_rects = math.sqrt(math.pow(pCenterX - qCenterX, 2.0)) + math.pow(pCenterY - qCenterY, 2.0)
        
                if dist_between_rects < 50:
                    if cv2.contourArea(pp) > cv2.contourArea(qq):
                        insidePolygons.append(q)
                    else:
                        insidePolygons.append(p)
                
        # naive algorithm        
        for i in insidePolygons:
            for j, p in enumerate(possiblePolygons):
                if i[0] is p[0]:
                    del possiblePolygons[j]
                    break
        
        for p, px, py, pw, ph in possiblePolygons:
            pCenterX = px + pw/2.0
            pCenterY = py + ph/2.0
            cvimg.draw_contour(p, self.candidateColor, 2)
            cvimg.draw_point((int(pCenterX), int(pCenterY)), 2, self.candidateColor)
        
        maxArea = 0.0
        biggest_rectangle = None
        
        # contour type
        for p in possiblePolygons:
            area = abs(cv2.contourArea(p[0]))
            if area >= maxArea:
                maxArea = area
                biggest_rectangle = p
                
        if biggest_rectangle is not None:
            
            b, bx, by, bw, bh = biggest_rectangle
            
            bCenterX = bx + bw/2.0
            bCenterY = by + bh/2.0
            cvimg.draw_contour(b, self.targetColor, 3)
            cvimg.draw_point((int(pCenterX), int(pCenterY)), 2, self.targetColor)
            
            angle_susan = (cvimg.width / 2.0 - bCenterX) * self.AXIS_CAMERA_VIEW_ANGLE / cvimg.width
            distance = (cvimg.width * 22.0) / (2.0 * bx * math.tan(self.AXIS_CAMERA_VIEW_ANGLE/2.0))
        
        return cvimg.img
