#breakdown mineral code
import cv2
import numpy as np
import time
import socket
import sys
import struct
fonttt=cv2.FONT_HERSHEY_SIMPLEX
fontScale=0.4
fontColor= (0,0,255)
lineType=2
HOST = '192.168.137.1'
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

def nothing():
    pass
Sensor_data={'Aspect Ratio':[],'Extent':[],'Solidity %':[],'Equivalent Diameter':[]}
df = pd.DataFrame(Sensor_data, columns= ['Aspect Ratio', 'Extent','Solidity %','Equivalent Diamtere'])
aspect_ratios=extents=solidity=equi_diameter=areaw=[]
scale=0.5;
#image=cv2.resize(image,(int(scale*image.shape[1]),int(scale*image.shape[0])))
#cv2.imshow('i',iml)
cv2.namedWindow('Gaussian')
cv2.resizeWindow('Gaussian',400,200)
cv2.createTrackbar('Filter','Gaussian',0,20,nothing)
cv2.createTrackbar('color_threshold','Gaussian',0,200,nothing)
cv2.createTrackbar('k_value','Gaussian',0,50,nothing)
#cv2.createTrackbar('lineType','Gaussian',1,10,nothing)
#cv2.createTrackbar('fontScale','Gaussian',0,1,nothing)
fil=3
ct=20
k_value=9
h=s=v=t=0
rock_number=0
all_properties=[]
cnt=0
def save_image(image1,image2,image3,cnt):
    cv2.imwrite('filtered_image'+str(cnt)+'.png',image1)
    #print('Image 1 saved.')
    cv2.imwrite('blurred_image'+str(cnt)+'.png',image2)
    #print('Image 2 saved.')
    cv2.imwrite('orignal_image'+str(cnt)+'.png',image3)
    #print('Image 3 saved.')
    cnt=cnt+1
    return(cnt)
    

def blur(image,blur_val):
    if(blur_val%2==0):
        blur_val+=1
        x=cv2.GaussianBlur(image,(blur_val,blur_val),0)
        cv2.imshow('Image',x)
        return(x)

    
def hsv_segmentation(blurred_image):
    x,y,w,h=cv2.selectROI(cv2.cvtColor(blurred_image,cv2.COLOR_BGR2HSV),False,False)
    ROI_image=blurred_image[y:y+h,x:x+w]
    h,s,v=cv2.split(cv2.cvtColor(ROI_image,cv2.COLOR_BGR2HSV))
    cv2.destroyWindow('Image')
    #cv2.imshow('x1',ROI_image)
    return(h,s,v)


def  color_filter(image,h,s,v,filter_val):
    lower=np.array([int(np.mean(h)-filter_val),int(np.mean(s)-filter_val),int(np.mean(v)-filter_val)])
    upper=np.array([int(np.mean(h)+filter_val),int(np.mean(s)+filter_val),int(np.mean(v)+filter_val)])
    filtered_image=cv2.inRange(cv2.cvtColor(image,cv2.COLOR_BGR2HSV),lower,upper)
    #cv2.imshow('color_based_filter',filtered_image)
    return(filtered_image)


def open_image(filter_image,k_value):
    kernel=np.ones((k_value,k_value),dtype=np.float32)/(k_value*k_value)
    removed_im=cv2.morphologyEx(filter_image,cv2.MORPH_OPEN,kernel)
    cv2.imshow('removed_im',removed_im)
    return(removed_im)
def aspect_ratio(a,b):
    return(float(a)/b)


def extent(cnt):
    area = cv2.contourArea(cnt)
    #areaw.append(cnt)
    x,y,w,h = cv2.boundingRect(cnt)
    rect_area = w*h
    hull = cv2.convexHull(cnt)
    hull_area = cv2.contourArea(hull)
    print((float(area)/rect_area),cv2.contourArea(cnt)
           ,float(area)/hull_area,np.sqrt(4*area/np.pi))
    return((float(area)/rect_area),cv2.contourArea(cnt)
           ,float(area)/hull_area,np.sqrt(4*area/np.pi))


  
def physical_params(removed_im):
    im2, contours, hierarchy = cv2.findContours(removed_im,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    print('Total contours detected= ',len(contours))
    for i in range(len(contours)):
        cnt=contours[i]
        x,y,w,h = cv2.boundingRect(cnt)
        val1=aspect_ratio(w,h)
        #print(extens,rock_area,solidityss,equivalent_dia)
        extens,rock_area,solidityss,equivalent_dia=extent(cnt)
        print(extens,rock_area,solidityss,equivalent_dia)
        return(val1,extens,rock_area,solidityss,equivalent_dia)


def text(removed_im,array_values):
    display_text='Aspect ratio: '+str(array_values[0])+' Extent: '+str(array_values[1])
    display_text3='Equivalent diameter: '+str(array_values[4])
    display_text2='Rock Area: '+str(array_values[2])+' Solidity: '+str(array_values[3])
    #print('done till here')
    imgf=cv2.putText(removed_im,display_text, (0,40),cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255,255,128),1)
    #print('done_done')
    imgf=cv2.putText(removed_im,display_text2, (0,60), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255,255,128),1)
    imgf=cv2.putText(removed_im,display_text3, (0,20), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255,255,128),1)
    cv2.imshow('p',imgf)
    return(imgf)
    

        
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
    image = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)    #USE THIS
    #ret,image=cam.read()
    k=cv2.waitKey(1)
    if k & 0xFF == ord('q'):
        break
    fil=cv2.getTrackbarPos('Filter','Gaussian')
    ct=cv2.getTrackbarPos('color_threshold','Gaussian')
    k_value=cv2.getTrackbarPos('k_value','Gaussian')
    #lineType=cv2.getTrackbarPos('lineType','Gaussian')
    #fontScale=cv2.getTrackbarPos('fontScale','Gaussian')
    blurred_image=blur(image,fil)
    if k==ord('s'):
        h,s,v=hsv_segmentation(blurred_image)
        #print(h,s,v)
        t=1
    if t==1:
        filter_image=color_filter(blurred_image,h,s,v,ct)
        removed_im=open_image(filter_image,k_value)
    #GRAUNOLOGY AND PHYSICAL IDENTIFICATION
    if k==ord('r'):
        array_values=physical_params(removed_im)
        #print(a,b,c,d,e)
        all_properties.append(array_values)
    if k==ord('x'):
        try:
            new_d=text(removed_im,array_values)
            cnt=save_image(new_d,blurred_image,image,cnt)
        except:
            print('No contours found.')
            pass
cv2.destroyAllWindows()
#s.close()
