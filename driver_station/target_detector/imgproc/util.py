

import cv2
import numpy as np

from common import enum

colorspace = enum(RGB=0, BGR=1, HSV=2, GRAY=3, LAB=4, LUV=5)

_conversions = [(None, cv2.COLOR_RGB2BGR, cv2.COLOR_RGB2HSV, cv2.COLOR_RGB2GRAY, cv2.COLOR_RGB2LAB, cv2.COLOR_RGB2LUV), # RGB
                (cv2.COLOR_BGR2RGB, None, cv2.COLOR_BGR2HSV, cv2.COLOR_BGR2GRAY, cv2.COLOR_BGR2LAB, cv2.COLOR_BGR2LUV), # BGR
                (cv2.COLOR_HSV2RGB, cv2.COLOR_HSV2BGR, None, -1, -1, -1),                                               # HSV
                (cv2.COLOR_GRAY2RGB, cv2.COLOR_GRAY2BGR, -1, None, -1, -1),                                             # GRAY
                (cv2.COLOR_LAB2RGB, cv2.COLOR_LAB2BGR, -1, -1, None, -1),                                               # LAB
                (cv2.COLOR_LUV2RGB, cv2.COLOR_LUV2BGR, -1, -1, -1, None)]


def cvt_colorspace(src, src_colorspace, dst_colorspace):
    '''
        Converts from one colorspace to another.
    '''
    
    conversion = _conversions[src_colorspace][dst_colorspace]
    if conversion == -1:
        raise TypeError("Conversion not supported between %s and %s" % (src_colorspace, dst_colorspace))
    
    elif conversion is not None:   
        if src_colorspace == colorspace.GRAY:
            dst = np.empty((src.shape[0], src.shape[1], 3), src.dtype)
        elif dst_colorspace == colorspace.GRAY:
            dst = np.empty((src.shape[0], src.shape[1], 1), src.dtype)
        else:
            dst = src
       
        cv2.cvtColor(src, conversion, dst)
        return dst
    
    return None

