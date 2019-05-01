import cv2
import numpy as np
import matplotlib.pyplot as plt
def nothing(x):
    pass
img1=cv2.imread('detect.jpg')
fig, ax = plt.subplots()
frame=cv2.imread('21 (1).png')
cv2.namedWindow('Properties')
cv2.resizeWindow('Properties',600,100)
cv2.createTrackbar('Gaussian blur','Properties',0,100,nothing)
cnt=0
def match_features(frame):
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    h,s,v=cv2.split(hsv)
    (hmax,hmin)=(np.mean(h)+50,np.mean(h)-50)
    (smax,smin)=(np.mean(s)+50,np.mean(s)-50)
    (vmax,vmin)=(np.mean(v)+50,np.mean(v)-50)
    lower=np.array((hmin,smin,vmin))
    upper=np.array((hmax,smax,vmax))
    temp=cv2.inRange(img1,lower,upper)
    matches=cv2.bitwise_and(img1,img1,mask=temp)
    #cv2.imshow('Matched',matches)
    cv2.imshow('Orignal',img1)
    ret,thresh = cv2.threshold(temp, 40, 255, 0)
    im2,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(contours, key = cv2.contourArea)
    x,y,w,h = cv2.boundingRect(c)
    cv2.rectangle(matches,(x,y),(x+w,y+h),(0,255,0),2)
    cv2.imshow('Matched',matches)
    return(matches)
    #h1,s1,v1=cv2.split(temp)
    #(h1max,h1min)=(np.max(h1),np.min(h1))
    #(s1max,hs1min)=(np.max(s1),np.min(s1))
    #(v1max,v1min)=(np.max(v1),np.min(v1))
bins =16
alpha = 0.5
ax.set_xlim(0, bins-1)
ax.set_ylim(0, 1)
resizeWidth =0

ax.set_title('Histogram (RGB)')
ax.set_xlabel('Bin')
ax.set_ylabel('Frequency')
lw = 3
lineR, = ax.plot(np.arange(bins), np.zeros((bins,)), c='r', lw=lw, alpha=alpha)
lineG, = ax.plot(np.arange(bins), np.zeros((bins,)), c='g', lw=lw, alpha=alpha)
lineB, = ax.plot(np.arange(bins), np.zeros((bins,)), c='b', lw=lw, alpha=alpha)
plt.ion()
plt.show()
while True:
    numPixels = np.prod(frame.shape[:2])
    (b, g, r) = cv2.split(frame)
    histogramR = cv2.calcHist([r], [0], None, [bins], [0, 255]) / numPixels
    histogramG = cv2.calcHist([g], [0], None, [bins], [0, 255]) / numPixels
    histogramB = cv2.calcHist([b], [0], None, [bins], [0, 255]) / numPixels
    lineR.set_ydata(histogramR)
    lineG.set_ydata(histogramG)
    lineB.set_ydata(histogramB)
    fig.canvas.draw()
    #cv2.imshow('frame',frame)
    k=cv2.waitKey(1)
    fill=cv2.getTrackbarPos('Gaussian blur','Properties')
    #numPixels = np.prod(frame.shape[:2])
    #print(fill)
    if fill%2!=0:
        try:
            blur=cv2.GaussianBlur(frame,(fill,fill),0)
            cv2.imshow('blur',blur)
            homography=match_features(blur)
        except Exception as e:
            print(e)
    cv2.imshow('frame',frame)
    if k & 0xFF == ord('q'):
        break
    elif k==ord('w'):
        print(cv2.imwrite('Image-'+str(cnt)+'.png',frame))
        print(cv2.imwrite('Gray Image-'+str(cnt)+'.png',blur))
        print(cv2.imwrite('Matched Image-'+str(cnt)+'.png',homography))
        #print(cv2.imwrite('Image-'+str(cnt)+'.png',frame))
    
