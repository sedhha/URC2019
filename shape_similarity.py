#shape similarity
import cv2
import numpy as np
img1 = cv2.imread('1.jpg',0)
img2 = cv2.imread('rocks2.jpg',0)
ret, thresh = cv2.threshold(img1, 127, 255,0)
ret, thresh2 = cv2.threshold(img2, 127, 255,0)
_,contours,hierarchy = cv2.findContours(thresh,2,1)
print(len(contours))
cnt1 = contours[0]
_,contours,hierarchy = cv2.findContours(thresh2,2,1)
print(len(contours))
cnt2 = contours[0]
ret = cv2.matchShapes(cnt1,cnt2,1,0.0)
print(ret)
