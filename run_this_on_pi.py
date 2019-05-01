#SENSOR_DATA_TRANSFER
import socket
import serial
host = "192.168.137.54"
port = 50007
import time 
mySocket = socket.socket()
mySocket.bind((host,port))
 
mySocket.listen(1)
conn, addr = mySocket.accept()
print ("Connection from: " + str(addr))
aD=serial.Serial('/dev/ttyACM0',9600)
while True:
    while (aD.inWaiting()==0):
        pass
    try:
        astring=str(aD.readline())
        #astring=str(aD.readline())
        astring=astring[2:]
        astring=astring[:-5]
        
        '''data = conn.recv(1024).decode()
        if not data:
                break
        print ("from connected  user: " + str(data))'''
         
        #data = str(data).upper()
        #print ("sending: " + str(data))
        conn.send(astring.encode())
        time.sleep(0.09)
    except:
        pass
         
conn.close()
