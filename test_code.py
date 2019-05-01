import cv2
import numpy as np
import math
full=cv2.imread('Final_stitch.PNG')
(i,j,k)=np.shape(full)
print(i,j)
col = j/179
#img1 = i*col-col*(90-i)
img0=np.delete(full,slice(math.floor(col*90),j),axis=1)
img89=np.delete(full,slice(0,math.floor(j-90*col)),axis=1)
#cv2.imshow('i1',img1)
#cv2.imshow('i90',img90)

cv2.imshow('imgy',imgy)
for ixd in range(1,89):
    imgx=np.delete(full,slice(0,math.floor(ixd*col)),axis=1)
    (x1,y1,z1)=np.shape(imgx)
    imgy=np.delete(imgx,slice(math.floor(90*col),y1),axis=1)
    cv2.imwrite('img'+str(ixd)+'.png',imgy)

    

