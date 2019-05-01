import socket               
import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt
from drawnow import *
plt.ion()
x=list()
def plotting():
    plt.plot(x,'b-',linewidth=3)
    plt.title('Depth variation across distance')
s = socket.socket()        
host = '192.168.137.54'# ip of raspberry pi 
port = 50007              
s.connect((host, port))
###############################################################
#Storage dictionary
Sensor_data={'Soil Temperature':[],'MQ-4':[],'Humidity %':[],'H2 concentration':[],
             'CO concentration':[],'Rock distance':[],'MQ-4 Atmosphere':[]}
df = pd.DataFrame(Sensor_data, columns= ['Soil Temperature', 'MQ-4','Humidity %','H2 concentration','CO concentration','Rock distance','MQ-4 Atmosphere'])
count=0
###############################################################
while (count<100):
    #time.sleep(0.1)
    #print(type(s.recv(1024).decode()))
    #print('Warming...')
    #time.sleep(3)
    data=s.recv(1024).decode()
    #print(len(data))
    #print('I got the data.')
    #print(len(data))
    if(len(data)>=30 and len(data)<=34):  #change it to 30 for madhukumar code
        #data=data[4:] #comment actual time
        array_val=data.split(',')
        print(array_val)
        Sensor_data['Soil Temperature'].append(int(array_val[0]))
        Sensor_data['MQ-4'].append(array_val[1])
        Sensor_data['Humidity %'].append(array_val[2])
        Sensor_data['H2 concentration'].append(array_val[3])
        Sensor_data['CO concentration'].append(array_val[4])
        Sensor_data['Rock distance'].append(array_val[5])
        Sensor_data['MQ-4 Atmosphere'].append(array_val[6])
        #Sensor_data['CO2 ppm value'].append(array_val[7])
        print(data)
        x.append(float(array_val[5]))
        drawnow(plotting)
        
        count=count+1
        #print(count,array_val)
df = pd.DataFrame(Sensor_data, columns= ['Soil Temperature', 'MQ-4','Humidity %','H2 concentration','CO concentration','Rock distance','MQ-4 Atmosphere'])
df.to_csv (r'E:\SAHIL\RW\urc19\Task wise approach\All_programs\SI_sensor_data_transfer\all_sensor_data_transfer\sensor_data.csv', index = None, header=True)
print('Task Done')
    #coma separated values soil temperature(degree celcius),MQ4(voltssoil),(%hum),(atom h2),(atom co), distance by US sensor,(atom ch4)
    #x=np.frombuffer(s.recv(1024), dtype=np.uint8)
s.close()

