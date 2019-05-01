%% section 1
mypi=raspi();
myCam=cameraboard(mypi,'Resolution','640x480');

%% section 2
%IMAGE ACQUISITION AND PLOTTING

mysnap=snapshot(myCam);
imshow(mysnap);
hold on

%% Detect face and insert rectangle
fD=vision.CascadeObjectDetector();
bbox=step(fD,mysnap);
imageout=insertObjectAnnotation(mysnap,'rectangle',bbox,'Face');
imshow(imageout);
title('Detected face');
%% continious loop
flag=1;
while flag
    clearvars -except mypi myCam flag
    mySnap=snapshot(myCam);
    imshow(mySnap);
    hold on
    fD=vision.CascadeObjectDetector();
    bbox=step(fD,mySnap);
    imageout=insertObjectAnnotation(mySnap,'rectangle',bbox,'Face');
    imshow(imageout);
    title('Detected Face');
    drawnow
end