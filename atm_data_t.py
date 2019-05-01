import socket               
import time
import matplotlib.pyplot as plt
from drawnow import *
import pandas as pd
import cv2
def plotting():
    plt.figure(1)
    plt.plot(atT,'b-',linewidth=3)
    plt.title('Temp across distance')
def plottingH():
    plt.figure(2)
    plt.plot(atH,'r-',linewidth=3)
    plt.title('Humidity across distance')
def plottingP():
    plt.figure(3)
    plt.plot(atP,'ro',linewidth=3)
    plt.title('P across distance')
plt.ion()
atT=atH=atP=list()
Sensor_data={'Atmosphere Temperature':[],'Atmosphere Humidity%':[],'Atmosphere Pressure':[]}
df = pd.DataFrame(Sensor_data, columns= ['Atmosphere Temperature', 'Atmosphere Humidity%','Atmosphere Pressure'])
#count=0
s = socket.socket()        
host = '192.168.1.106'# ip of raspberry pi 
port = 50007              
s.connect((host, port))
while True:
    k=cv2.waitKey(1)
    data=s.recv(1024).decode()
    array_val=data.split(',')
    if len(array_val)>3:
        print(len(array_val))
        pass
    try:
        atT.append(float(array_val[0]))
        atH.append(float(array_val[1]))
        atP.append(float(array_val[2]))
        Sensor_data['Atmosphere Temperature'].append(float(array_val[0]))
        Sensor_data['Atmosphere Humidity%'].append(float(array_val[1]))
        Sensor_data['Atmosphere Pressure'].append(float(array_val[2]))
        print(array_val)
        plt.subplot(311)
        plt.plot(atT,'b-',linewidth=3)
        plt.subplot(312)
        plt.plot(atH,'r-',linewidth=3)
        plt.subplot(313)
        plt.plot(atP,'ro',linewidth=3)
        plt.pause(1)
    except:
        pass
    if k==ord('s'):
        break
df = pd.DataFrame(Sensor_data, columns= ['Atmosphere Temperature', 'Atmosphere Humidity%','Atmosphere Pressure'])
df.to_csv (r'E:\SAHIL\RW\urc19\Task wise approach\arduino\Matlab_soil_box\atmosphere_data.csv', index = None, header=True)
print('Task Done')
    
