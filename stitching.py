import cv2
import numpy as np
im1=cv2.imread('E:\SAHIL\RW\complete science task\MATLAB codes\p1.jpg')
im2=cv2.imread('E:\SAHIL\RW\complete science task\MATLAB codes\p2.jpg')
rows1 = im1.shape[0]    
rows2 = im2.shape[0]
if rows1 < rows2:
        im1 = np.concatenate((im1,np.zeros((rows2-rows1,im1.shape[1]))), axis=0)
if rows1 > rows2:
    im2 = np.concatenate((im2,np.zeros((rows1-rows2,im2.shape[1]))), axis=0)
    # if none of these cases they are equal, no filling needed.

cv2.imshow(np.concatenate((im1,im2), axis=1))
