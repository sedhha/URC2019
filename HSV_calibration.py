import cv2
import numpy as np
#cv2.resizeWindow('image',640,320)
#i=cv2.imread('MK1.jpg')
cam=cv2.VideoCapture(0)
def nothing(x):
    pass
cv2.namedWindow('Set properties')
cv2.resizeWindow('Set properties',400,400)
cv2.createTrackbar('H','Set properties',0,255,nothing)
cv2.createTrackbar('S','Set properties',0,255,nothing)
cv2.createTrackbar('V','Set properties',0,255,nothing)
cv2.createTrackbar('HM','Set properties',0,255,nothing)
cv2.createTrackbar('SM','Set properties',0,255,nothing)
cv2.createTrackbar('VM','Set properties',0,255,nothing)
HSV1=(0,0,104)
HSV2=(136,147,153)
#Soil types: gray: 95 36 74 107 110 172 mountain: 5 8 160 36 39 171
# light soil 0 4 119 176 52 159 dark soil 0 0 47 126 76 167 water bodies 0 0 99 155 78 151
def calibrate(img):
    #print('Loop in')
    r=cv2.selectROI("SELECTROI",img,False,False)
    
    cropped=cv2.cvtColor(img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])],cv2.COLOR_BGR2HSV)
    cv2.imshow('cropped',cropped)
    (h,s,v)=cv2.split(cropped)
    print(np.min(h),np.min(s),np.min(v),np.max(h),np.max(s),np.max(v))
num=0

while True:
    ret,frame=cam.read()
   #frame=i
    small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
    k=cv2.waitKey(1)
    if k==ord('c'):
        calibrate(small)
    H=cv2.getTrackbarPos('H','Set properties')
    S=cv2.getTrackbarPos('S','Set properties')
    V=cv2.getTrackbarPos('V','Set properties')
    HM=cv2.getTrackbarPos('HM','Set properties')
    SM=cv2.getTrackbarPos('SM','Set properties')
    VM=cv2.getTrackbarPos('VM','Set properties')
    image=cv2.inRange(cv2.cvtColor(small,cv2.COLOR_BGR2HSV),(H,S,V),(HM,SM,VM))
    cv2.imshow('image',small)
    cv2.imshow('INRANGE',image)
    #cv2.imshow('Frame',i)

    
