%HISTOGRAM_EQUILIZATION
close all
img_src=imread('1.jpeg');
%ref=imread('2.jpg');
%cam=webcam(1);
v=VideoReader('testcasem4.mp4');
cnt=1;
while hasFrame(v)
ref = readFrame(v);
imgr=img_src(:,:,1);
imgg=img_src(:,:,2);
imgb=img_src(:,:,3);

imgr1=ref(:,:,1);
imgg1=ref(:,:,2);
imgb1=ref(:,:,3);

Hnimgr=imhist(imgr);
Hnimgg=imhist(imgg);
Hnimgb=imhist(imgb);

Hnimgr1=imhist(imgr1);
Hnimgg1=imhist(imgg1);
Hnimgb1=imhist(imgb1);

outr=histeq(imgr,Hnimgr1);
outg=histeq(imgg,Hnimgg1);
outb=histeq(imgb,Hnimgb1);

histsp(:,:,1)=outr;
histsp(:,:,2)=outg;
histsp(:,:,3)=outb;

figure(1);
subplot(331);plot(Hnimgr);title('R input');
subplot(334);plot(Hnimgg);title('G input');
subplot(337);plot(Hnimgb);title('B input');
subplot(332);plot(Hnimgr1);title('R ref');
subplot(335);plot(Hnimgg1);title('G ref');
subplot(338);imshow(ref);title('Video feed');
subplot(333);imhist(outr);title('R result');
subplot(336);imhist(outg);title('G result');
subplot(339);imhist(outb);title('B result');
%subplot(141);imshow(ref);title('Image feed');
%subplot(142);imhist(outr);title('Red result');
%subplot(143);imhist(outg);title('Red result');
%subplot(144);imhist(outr);title('Red result');
drawnow
%figure(2);
%imshow(ref);
drawnow
end