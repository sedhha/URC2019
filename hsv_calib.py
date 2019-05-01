import cv2
import numpy as np
def nothing(x):
    pass
cv2.namedWindow('Image Analysis')
cv2.createTrackbar('H','Image Analysis',0,255,nothing)
cv2.createTrackbar('S','Image Analysis',0,255,nothing)
cv2.createTrackbar('V','Image Analysis',0,255,nothing)
cv2.createTrackbar('HM','Image Analysis',0,255,nothing)
cv2.createTrackbar('SM','Image Analysis',0,255,nothing)
cv2.createTrackbar('VM','Image Analysis',0,255,nothing)
img=cv2.imread('example.jpg')
while True:
    k=cv2.waitKey(1)
    frame=img
    h=cv2.getTrackbarPos('H','Image Analysis')
    s=cv2.getTrackbarPos('S','Image Analysis')
    v=cv2.getTrackbarPos('V','Image Analysis')
    hm=cv2.getTrackbarPos('HM','Image Analysis')
    sm=cv2.getTrackbarPos('SM','Image Analysis')
    vm=cv2.getTrackbarPos('VM','Image Analysis')
    lower=np.array([h,s,v])
    upper=np.array([hm,sm,vm])
    filtered=cv2.inRange(frame,lower,upper)
    cv2.imshow('frame',filtered)
    cv2.imshow('actual',frame)
