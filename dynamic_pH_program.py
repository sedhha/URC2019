#dynamic
import cv2
import numpy as np
import time
import socket
import sys
import numpy as np
import struct

HOST = '192.168.137.1' #change it every time
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


#import matplotlib.pyplot as plt
def nothing(x):
    pass
img1=cv2.imread('detect.jpg')
#frame=cv2.imread('22.jpg')
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
    
    
while True:
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
    #cv2.imshow('frame',frame)
    k=cv2.waitKey(1)
    fill=cv2.getTrackbarPos('Gaussian blur','Properties')
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
    
