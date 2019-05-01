#HSV_INRANGEFINDER
import cv2
import numpy as np
def nothing(x):
    pass
cv2.namedWindow('Image filtering')
cv2.createTrackbar('I1','Image filtering',0,255,nothing)
cv2.createTrackbar('I2','Image filtering',0,255,nothing)
cv2.createTrackbar('I3','Image filtering',0,255,nothing)
cv2.createTrackbar('I4','Image filtering',0,255,nothing)
cv2.createTrackbar('I5','Image filtering',0,255,nothing)
cv2.createTrackbar('I6','Image filtering',0,255,nothing)
lower=np.array([0,0,0])
higher=np.array([255,255,255])
cam=cv2.VideoCapture(0)
while True:
    k=cv2.waitKey(1)
    if k & 0xFF==ord('q'):
        break
    _,frame=cam.read()
    i1=cv2.getTrackbarPos('I1','Image filtering')
    i2=cv2.getTrackbarPos('I2','Image filtering')
    i3=cv2.getTrackbarPos('I3','Image filtering')
    i4=cv2.getTrackbarPos('I4','Image filtering')
    i5=cv2.getTrackbarPos('I5','Image filtering')
    i6=cv2.getTrackbarPos('I6','Image filtering')
    #print(i1,i2,i3,i4,i5,i6)
    lower=np.array([i1,i3,i5])
    upper=np.array([i2,i4,i6])
    filtered=cv2.inRange(frame,lower,upper)
    try:
        cv2.imshow('Filtered',filtered)
    except:
        pass
