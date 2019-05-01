import cv2
import numpy as np
import matplotlib.pyplot as plt
img=cv2.imread('tmp1.jpg')
mask=np.zeros(img.shape[:2],np.uint8)
bgModel=np.zeros((1,65),np.float64)
fgModel=np.zeros((1,65),np.float64)
rect=(161,79,150,150)
cv2.grabCut(img,mask,rect,bgModel,fgModel,5,cv2.GC_INIT_WITH_RECT)
mask2=np.where((mask==2)|(mask==0),0,1).astype('uint8')
img=img*mask2[:,:,np.newaxis]
plt.imshow(img)
plt.colorbar()
plt.show()
