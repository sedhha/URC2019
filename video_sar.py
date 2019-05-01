
































import numpy as np
import cv2
import time
cam=cv2.VideoCapture('testcasem4.mp4')
ret=True
tk=0
while ret:
    try:
        ret,frame=cam.read()
        retval, threshold = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY_INV)
        cv2.imshow('Heat affected zones',threshold)
        cv2.imshow('Actual image',frame)
        if tk==0:
            time.sleep(10)
            tk=1
        k=cv2.waitKey(1)
        if k & 0xFF==ord('q'):
            break
    except:
        ret=False
