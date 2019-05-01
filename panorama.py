#static image
import cv2
import numpy as np
import time
import socket
import sys
import numpy as np
import struct
HOST = '192.168.1.108' #change it every time
PORT=8089
cnt=0
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print ('Socket created')
s.bind((HOST,PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')
conn,addr=s.accept()
data = b""
payload_size = struct.calcsize("q")
count=0
def nothing(x):
    pass

cv2.namedWindow('Properties')
cv2.resizeWindow('Properties',600,200)
cv2.createTrackbar('Image-1 width','Properties',0,1000,nothing)
cv2.createTrackbar('Image-2 width','Properties',0,1000,nothing)


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
    ic2=np.delete(image2,slice(0,val2),axis=1)
    cv2.imshow('image-2',ic2)
    return(ic1,ic2)
def stitch(ic1,ic2):
    ixf=np.concatenate((ic1,ic2),axis=1)
    return(ixf)
#image=cv2.imread('ex0.jpg')
#image2=cv2.imread('ex1.jpg')
#image3=cv2.imread('ex2.jpg')
ill=0
while True:
    val1=cv2.getTrackbarPos('Image-1 width','Properties')
    val2=cv2.getTrackbarPos('Image-2 width','Properties')
    while len(data) < payload_size:
        data += conn.recv(4096)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    #print(packed_msg_size)
    msg_size = struct.unpack("q", packed_msg_size)[0]
    #print(msg_size)
    while len(data) < msg_size:
        data += conn.recv(4096)
        # print('Rec 2')
    frame_data = data[:msg_size]
    data = data[msg_size:]
    # frame=pickle.loads(frame_data)
    frame_data = np.fromstring(frame_data, np.uint8)      #USE THIS
    frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)    #USE THIS
    #_,frame=cam.read()'''
    k=cv2.waitKey(1)
    if k & 0xFF==ord('q'):
        break
    cv2.imshow('frame',frame)        
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
            stitch_1=stitch(ic1,ic2)
            cv2.imshow('First stitch',stitch_1)
        except Exception as e:
            print(e)
    elif count==2:
        try:
            ic1,ic2=align(stitch_1,image2,val1,val2)
            final=stitch(ic1,ic2)
            cv2.imshow('Final stitch',final)
        except Exception as e:
            print(e)
    elif count>2:
        cv2.imwrite('stitched_paranoma.png',final)
        break
                
            
        



        
                   
        
        

