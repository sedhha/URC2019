import cv2
import numpy as np
cap=cv2.VideoCapture(0)
while True:
    _,frame=cap.read()
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    lower_red=np.array([105,105,0])
    upper_red=np.array([150,255,255])
    #dark_red=np.uint8([[[12,22,121]]])
    #dark_red=cv2.cvtColor(dark_red,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,lower_red,upper_red)
    res=cv2.bitwise_and(frame,frame,mask=mask)
    #cv2.imshow('frame',frame)
    #cv2.imshow('mask',mask)
    
    #erosions########
    kernel=np.ones((5,5),np.uint8)
    erosion=cv2.erode(mask,kernel,iterations=1)
    dilation=cv2.dilate(mask,kernel,iterations=1)
    cv2.imshow('result',res)
    cv2.imshow('frame',frame)
    cv2.imshow('erosion',erosion)
    cv2.imshow('dilation',dilation)
    #################
    ######opening###
    opening=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel)
    closing=cv2.morphologyEx(mask, cv2.MORPH_CLOSE,kernel)
    cv2.imshow('opening',opening)
    cv2.imshow('closing',closing)
    ############
    ##top hat black hat#####
    
    #cv2.imshow('Tophat',tophat)
    #cv2.imshow('Blackhat',blackhat)
    #kernel=np.ones((15,15),np.float32)/225
    blur=cv2.GaussianBlur(res,(15,15),0)
    median=cv2.medianBlur(res,15)
    smoothed=cv2.bitwise_and(frame,frame,mask=mask)
    k=cv2.waitKey(5) &0xFF
    if k==27:
        break
cv2.destroyAllWindows()
cap.release()
