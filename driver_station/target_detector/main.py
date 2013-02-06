
import math
import os.path

from optparse import OptionParser
import cv2
import numpy as np

from imgproc import CvImg, CvContour, colorspace

def process_image(img):
    cvimg = CvImg(img, colorspace.BGR)
    
    # TODO: image processing goes here
    
    #cvimg.set_colorspace(colorspace.GRAY)
    #cvimg.equalize_hist()
    
    #cvimg.set_colorspace(colorspace.LAB)
    
    #for i, c in enumerate(cvimg.split()):
    #    c.threshold_otsu()
    #    c.show(str(i))
    
    cvimg.show('test')
    

def last_year(img):
    
    # TODO: This doesn't quite work yet
    
    # TODO: Need to split the detection and the contour processing algorithm
    
    # TODO: Perhaps use a different contour processing algorithm, or hough lines
    # to find the objects even if we can't see the whole object? 
    
    cvimg = CvImg(img, colorspace.BGR)
    
    b, g, r = cvimg.split()
    
    b.threshold(0)
    g.threshold(203)
    r.threshold(170)
    
    final = b.bitwise_and(r).bitwise_and(g)
    
    final.dilate(6)
    
    polygons = []
    contours = final.find_contours()
    
    for contour in contours:
        contour = CvContour(contour)
        ratio = contour.h / contour.w
        if ratio < 2 and ratio > 0.6:
            polygon = contour.approxPoly(45)
            polygons.append(polygon)
    
    possiblePolygons = []
    for polygon in polygons:
        if p is convex and len(p) == 4:
            possiblePolygons.append(polygon)
    
            
    results = []
    for p in polygons:
        for q in polygons:
            if p is q:
                continue
            
            pCenterX = p.x + p.w / 2
            qCenterX = q.x + q.w / 2
            pCenterY = p.y + p.h / 2
            qCenterY = q.y + q.h / 2 
            
            dist_between_rects = math.sqrt(math.pow(pCenterX - qCenterX, 2)) + math.pow(pCenterY - qCenterY, 2)
    
            if dist_between_rects < 50:
                if p.getArea() > q.getArea():
                    results.append(p)
                else:
                    results.append(q)
    
    maxArea = 0.0
    biggest_rect = None
    
    # contour type
    for p in results:
        if abs(p.getArea()) >= maxArea:
            maxArea = abs(p.getArea)
            biggest_rect = p
            
    if biggest_rect is not None:
        # draw polygon
        
        # draw center x, center y
        
        # x coordinate of the center
        center_x = biggest_rect.getX() + biggest_rect.getWidth()/2
        biggest_rect_w = biggest_rect.getWidth()
        
        # x in a relative coordinate system (-1,1)
        # x = (2 * x/rawImage.getWidth())
        
        angle_susan = (image_width / 2.0 - center_x) * AXIS_CAMERA_VIEW_ANGLE / image_width
        distance = (image_width * 22.0) / (2.0 * biggest_rectangle_width * math.tan(AXIS_CAMERA_VIEW_ANGLE/2.0))
        
        
    
    cvimg.show('test')
    
    
def user_save_image(img):
    
    # TODO: the image freezes while this is waiting for input. Fix that. 
    
    # Hehe. 
    timg = img.copy()
    h, w = timg.shape[:2]
    cv2.putText(timg, 'OH SNAP!', (w/6,h/2), cv2.FONT_HERSHEY_COMPLEX, 3, (255,255,255), 4)
    
    cv2.imshow('test', timg)
    cv2.waitKey(1)
    
    while True:
        filename = raw_input('Save to .png: ')
    
        if filename == '':
            continue
    
        if not filename.endswith('.png'):
            filename = filename + '.png'
            
        filename = os.path.abspath(filename)
    
        if os.path.exists(filename):
            overwrite = False
            while True:
                yn = raw_input("'%s' exists! Overwrite? [y/n] " % filename).lower()
                if yn == 'y':
                    overwrite = True
                    break
                elif yn == 'n':
                    break
                
            if not overwrite:
                continue
    
        if cv2.imwrite(filename, img):
            print "Image saved to '%s'" % filename
            break
        else:
            print "Error writing to '%s'!" % filename

    
class FakeCapture(object):
    '''Pretend to be a VideoCapture device... the synth option doesn't seem to work'''
    def __init__(self, filename):
        self.cvimg = CvImg.from_file(filename)
        
    def read(self):
        return True, self.cvimg.img.copy()
    


if __name__ == '__main__':
    
    parser = OptionParser()
    
    parser.add_option('-i',
                      dest='static_image', default=None,
                      help='Specify an image file to process')
    
    parser.add_option('--ip', dest='ip_address', default='10.24.23.11',
                      help='Specify the IP address of the camera')
    
    options, args = parser.parse_args()
    
    
    if options.static_image is not None:
        print "Opening %s" % options.static_image
        vc = FakeCapture(options.static_image)
    else:      
        print "Beginning capture"  
        vc = cv2.VideoCapture('rtsp://%s/axis-media/media.amp' % options.ip_address)
        
    print 'Starting processing. Press ESC to exit, or SPACE to save the current image'
    
    save = False
    
    while True:
        retval, img = vc.read()
        if retval:
            
            if save:
                user_save_image(img)
                save = False
            
            cvimg = process_image(img)
        else:
            print "No image acquired, exiting!"
            break
        
        key = 0xff & cv2.waitKey(1)
        if key == 27:
            break
        
        if key == ord(' '):
            save = True
        
    cv2.destroyAllWindows()
    print "Done."
    
