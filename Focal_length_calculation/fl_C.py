import cv2
import numpy as np

cam=cv2.VideoCapture(0)

while True:
    k=cv2.waitKey(1)
    if k & 0xFF==ord('q'):
        break
    _,frame=cam.read()
    img=cv2.inRange(frame,np.array([0,0,0]),np.array([180,255,30]))
    im2,contours,hierarchy = cv2.findContours(img, 1, 2)
    for i in range(len(contours)):
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        if area>200:
            print(area)
    cv2.imshow('Image',img)
