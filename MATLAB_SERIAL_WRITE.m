%SERIAL WRITE
clear all
close all
clc
mypi=raspi('192.168.137.5','pi','dpi123dpi');
myserialdevice=serialdev(mypi,'/dev/ttyUSB0',9600);
%write(myserialdevice,[10 12],'uint16')
%char(read(myserialdevice,65));
%char(read(myserialdevice,65));
read(myserialdevice,70);
read(myserialdevice,70);
for i=1:10
    x=input('Enter the serial data: [0,14]');
    
    disp('Serially written the data');
    temp=string(extractBetween(char(read(myserialdevice,70)),'(*)','*V*'));
    disp(strsplit(string(temp),','));
end