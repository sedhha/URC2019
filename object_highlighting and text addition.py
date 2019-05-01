import numpy as np
import cv2

img=cv2.imread('1.jpg',cv2.IMREAD_COLOR)
cv2.line(img,(0,0),(150,150),(0,255,0),15)
cv2.rectangle(img,(15,25),(200,150),(0,255,255),5)
cv2.circle(img,(120,45),55,(0,240,0),-1)
pts=np.array([[10,35],[40,30],[200,333],[230,600],[230,400],[190,450]],np.int32)
#pts=pts.reshape((-1,1,2))
cv2.polylines(img,[pts],True,(0,255,200),3)
font=cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(img,'Opencv sikho',(0,130),font,1,(200,255,255),2,cv2.LINE_AA)
cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
