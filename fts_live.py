import numpy as np
import cv2
import time
import socket
import sys
import numpy as np
import struct
#import time
tn=0

HOST = '192.168.43.217' #IP of the laptop
PORT=8089

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print ('Socket created')
s.bind((HOST,PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')
conn,addr=s.accept()

data = b""
payload_size = struct.calcsize("q")


#cam=cv2.VideoCapture(0)
ret=True
font=cv2.FONT_HERSHEY_SIMPLEX
fontScale=0.6
fontColor= (0,255,0)
lineType=1
def nothing(x):
    pass

def move_to_site(img,cx,cy):
    [x,y,z]=np.shape(img)
    #print(x,y)
    #time.sleep(2)
    if(cx>=0 and cx<(y/2)-20):
        print("----------------------------------------->Navigate Left<-----------------------------------------------")
    elif(cx>=(y/2)-20 and cx<=(y/2)+20):
        print("----------------------------------------->Navigate Straight<------------------------------------------")
    else:
        print("----------------------------------------->Navigate Right<---------------------------------------------")
        
    #print(cx,cy,(x/2),(y/2))

def density_selection(frame,val):
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    #cv2.imshow('hsv',hsv)
    lower=np.array([0,110,31])
    upper=np.array([12,236,152])
    hsv=cv2.inRange(hsv,lower,upper)
    #cv2.imshow('hsv',hsv)
    
    frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    ret,thresh=cv2.threshold(frame,val,255,cv2.THRESH_BINARY)  #Lower value for reducing density
    masked=cv2.bitwise_and(frame,frame,mask=thresh)
    masked2=cv2.bitwise_and(masked,masked,mask=hsv)
    ret,masked2=cv2.threshold(masked2,0,255,cv2.THRESH_BINARY)
   #cv2.imshow('density_match',thresh)
    ret,t2=cv2.threshold(masked2,val,255,cv2.THRESH_BINARY)
    cv2.imshow('masked_2',t2)
    return(t2,masked2)
amax=ind=0
amaxcanny=indcanny=0


def finalize(thresh):
    amax=0
    im2, cc, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cc, key = cv2.contourArea)
    for i in range(len(cc)):
        if amax<cv2.contourArea(cc[i]):
            amax=cv2.contourArea(cc[i])
            ind=i
    #x,y,w,h = cv2.boundingRect(c)
    M = cv2.moments(cc[ind])
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    return(thresh,amax,cx,cy)



def distance_navigation(img,cx,cy,Area):
     imgf=cv2.circle(img,(int(cx), int(cy)), 4, (0,255,0), -1)
     display_text='Distance value :  '+str(999999/Area)
     dp2=' with confidence level: '+str((Area/100000)+0.5)
     move_to_site(img,cx,cy)
     if(999999/Area<=20):
         site_located(img,int(999999/Area),cx,cy)
     imgf=cv2.putText(imgf,display_text, (cx-40,cy-10), font, fontScale,fontColor,lineType)
     imgf=cv2.putText(imgf,dp2, (cx-40,cy+10), font, 0.5,(0,0,255),lineType)
     return(imgf)



def site_located(img,area,cx,cy):
    global tn
    imgx=cv2.circle(img,(int(cx), int(cy)), 4, (0,255,0), -1)
    display_text='Spot located'
    imgf=cv2.putText(imgx,display_text, (cx-40,cy-10), font, 0.8,(0,0,255),2)
    cv2.imshow('Spot detected.',imgx)
    #print(cv2.imwrite('spot'+str(tn)+'.jpg',imgx))
    tn=tn+1


    
    


def open_image(filter_image,k_value):
    kernel=np.ones((k_value,k_value),dtype=np.float32)/(k_value*k_value)
    removed_im=cv2.morphologyEx(filter_image,cv2.MORPH_OPEN,kernel)
    cv2.imshow('filtered Image',removed_im)
    return(removed_im)






def cannyedge(frame,valL,valH,iterations,LowT,HighT):
    retval, threshold = cv2.threshold(frame, LowT, HighT, cv2.THRESH_BINARY)
    erode = cv2.erode(threshold,None,iterations)
    dilate = cv2.dilate(threshold,None,iterations)
    edges_new = cv2.Canny(erode, valL, valH)
    #cv2.imshow('edges',edges_new)
    #cv2.imshow('edg',threshold)
    #cv2.imshow('edge',erode)
    image,contours,hierarchy=cv2.findContours(edges_new, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    final_thresh1,amax,cx,cy=finalize(edges_new)
    return(final_thresh1,amax,cx,cy)
    
    





    
cv2.namedWindow('Set properties')
cv2.resizeWindow('Set properties',400,400)
cv2.createTrackbar('Density','Set properties',0,255,nothing)
cv2.createTrackbar('Open','Set properties',0,100,nothing)
cv2.createTrackbar('Canny Edge L','Set properties',0,255,nothing)
cv2.createTrackbar('Canny Edge H','Set properties',0,255,nothing)
cv2.createTrackbar('Canny Edge I','Set properties',0,10,nothing)
cv2.createTrackbar('Low T','Set properties',0,255,nothing)
cv2.createTrackbar('High T','Set properties',0,255,nothing)
switch = '0 : OFF \n1 : ON'
cv2.createTrackbar(switch, 'Set properties',0,1,nothing)
LowT=HighT=val=valH=valL=iterations=opening_threshold=0
cntt=0    
      
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
    #ret,frame=cam.read()
    '''if ret==False:
        break'''
    k=cv2.waitKey(1)
    if k & 0xFF==ord('q'):
        break
    cv2.imshow('video',frame)
    val=cv2.getTrackbarPos('Density','Set properties')
    opening_threshold=cv2.getTrackbarPos('Open','Set properties')
    valH=cv2.getTrackbarPos('Canny Edge L','Set properties')
    valL=cv2.getTrackbarPos('Canny Edge H','Set properties')
    LowT=cv2.getTrackbarPos('Low T','Set properties')
    HighT=cv2.getTrackbarPos('High T','Set properties')
    iterations=cv2.getTrackbarPos('Canny Edge I','Set properties')
    try:
        ft1,amx,cxc,cyc=cannyedge(frame,valL,valH,iterations,LowT,HighT)
        navig_image_canny=cv2.bitwise_and(frame,frame,mask=ft1)
        navig_image1_canny=distance_navigation(navig_image_canny,cxc,cyc,amx)
        cv2.imshow('Navigation-Water trench',navig_image1_canny)
    except Exception as e:
        #print(e)
        pass
    thresh,masked=density_selection(frame,val)
    thresh=open_image(thresh,opening_threshold)
    #For selecting the best site
    try:
        final_thresh1,amax,cx,cy=finalize(thresh)
        navig_image=cv2.bitwise_and(frame,frame,mask=final_thresh1)
        navig_image1=distance_navigation(navig_image,cx,cy,amax)
        cv2.imshow('Navigation',navig_image1)
    except  Exception as e:
        #print(e)
        pass
    if k==ord('w'):
        cntt=cntt+1
        print(cv2.imwrite('Density_Navigation '+str(cntt)+'.png',navig_image1))
        print(cv2.imwrite('Water_trench_Navigation '+str(cntt)+'.png',navig_image1_canny))
        #print(cv2.imwrite('Water_trench_Navigation '+str(cntt)+'.png',navig_image1_canny))

    
    
