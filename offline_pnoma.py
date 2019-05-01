#static image
import cv2
import numpy as np
import time
cnt=0
count=0
def nothing(x):
    pass
cv2.namedWindow('Properties')
cv2.resizeWindow('Properties',600,200)
cv2.createTrackbar('Image-1 width','Properties',0,1000,nothing)
cv2.createTrackbar('Image-2 width','Properties',0,1000,nothing)
image=cv2.imread('Image-0.jpg')
image1=cv2.imread('Image-1.jpg')
image2=cv2.imread('Image-2.jpg')
cam=cv2.VideoCapture(0)
def align(image1,image2,val1,val2):            
    temp=cv2.cvtColor(image1,cv2.COLOR_BGR2GRAY)
    (a,b)=np.shape(temp)
    temp=cv2.cvtColor(image2,cv2.COLOR_BGR2GRAY)
    (c,d)=np.shape(temp)
    #print('seems cool')
    
    if(a!=c):
        if (a<c):
            image2=np.delete(image2,slice(a,c),axis=0)
        else:
            image1=np.delete(image1,slice(c,a),axis=0)
    ic1=np.delete(image1,slice(val1,b),axis=1)
    cv2.imshow('image-1',ic1)
    #print('Things cool till now')
    ic2=np.delete(image2,slice(0,val2),axis=1)
    cv2.imshow('image-2',ic2)
    
    return(ic1,ic2)
def stitch(ic1,ic2):
    ixf=np.concatenate((ic1,ic2),axis=1)
    return(ixf)
image=cv2.imread('p1.jpg')
image1=cv2.imread('p2.jpg')
image2=cv2.imread('p3.jpg')
#cv2.imshow('i1',image)
ill=0
while True:
    #_,frame=cam.read()
    #cv2.imshow('f',frame)
    val1=cv2.getTrackbarPos('Image-1 width','Properties')
    val2=cv2.getTrackbarPos('Image-2 width','Properties')
    k=cv2.waitKey(1)
    if k & 0xFF==ord('q'):
        break
    #cv2.imshow('frame',frame)        
    if k==ord('c'):
        cv2.imwrite('Image-'+str(cnt)+'.jpg',frame)
        if cnt==0:
            image=frame
            print(cv2.imwrite('first _image.jpg',image))
            print('Image 1 captured/')
            time.sleep(2)
        if cnt==1:
            image1=frame
            print('Image 2 captured/')
            print(cv2.imwrite('second _image.jpg',image1))
            time.sleep(2)
        if cnt==2:
            image2=frame
            print('Image 3 captured/')
            print(cv2.imwrite('third _image.jpg',image2))
            time.sleep(2)
        cnt=cnt+1
    if k==ord('s'):
        count=count+1
    if count==1:
        try:
            ic1,ic2=align(image,image1,val1,val2)
            #print('Error here')
            stitch_1=stitch(ic1,ic2)
            cv2.imshow('First stitch',stitch_1)
        except Exception as e:
            print(e)
            #print('Begin the slicing bro')
            pass
    elif count==2:
        try:
            ic1,ic2=align(stitch_1,image2,val1,val2)
            final=stitch(ic1,ic2)
            cv2.imshow('Final stitch',final)
        except Exception as e:
            print(e)
            pass
    elif count>2:
        cv2.imwrite('stitched_paranoma.png',final)
                
            
        



        
                   
        
        

