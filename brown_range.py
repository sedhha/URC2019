import cv2
import numpy as np
def nothing(x):
    pass
cv2.namedWindow('Set properties')
cv2.resizeWindow('Set properties',400,400)
cv2.createTrackbar('H','Set properties',0,255,nothing)
cv2.createTrackbar('S','Set properties',0,255,nothing)
cv2.createTrackbar('V','Set properties',0,255,nothing)
cv2.createTrackbar('HH','Set properties',0,255,nothing)
cv2.createTrackbar('SH','Set properties',0,255,nothing)
cv2.createTrackbar('VH','Set properties',0,255,nothing)

#img=cv2.imread(r'E:\SAHIL\RW\urc19\Task wise approach\sample\sample4.jpeg')
#cv2.imshow('image',img)
def hsv_range(img,Hval,Sval,Vval,HHal,SHal,VHal):
    cv2.imshow('hsv',img)
    #lower=np.array((Hval,Sval,Vval))
    #upper=np.array((HHal,SHal,VHal))
    #print(lower)
    #print(upper)
    lower=np.array([Hval,Sval,Vval])
    upper=np.array([HHal,SHal,VHal])
    img=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    img=cv2.inRange(img,lower,upper)
    cv2.imshow('img',img)
while True:
    k=cv2.waitKey(1)
    cv2.imshow('frame',img)
    #fv=cv2.flip(img,0)
    cv2.imshow('fv',img)
    if k==ord('q'):
        break
    Hval=cv2.getTrackbarPos('H','Set properties')
    Sval=cv2.getTrackbarPos('S','Set properties')
    Vval=cv2.getTrackbarPos('V','Set properties')
    HHal=cv2.getTrackbarPos('HH','Set properties')
    SHal=cv2.getTrackbarPos('SH','Set properties')
    VHal=cv2.getTrackbarPos('VH','Set properties')
    try:
        hsv_range(img,Hval,Sval,Vval,HHal,SHal,VHal)
    except Exception as e:
        print(e)
