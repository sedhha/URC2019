import socket
import time
f= open("atm_T.txt","w")
s = socket.socket()   
host = '192.168.1.164'# ip of raspberry pi 
port = 50007              
s.connect((host, port))
'''for i in range(1,10):
    f.write('temperature,humidity,atmosphere\n')'''
count=0
while (count<100):
    count=count+1
    
    data=s.recv(1024).decode()
    print(len(data))
    if len(data)>=30and len(data)<=45:
        print(data)
        f.write(data+'\n')
        #print(type(data))
    #print(len(data))
f.close()
print('Done')
#f.close()
