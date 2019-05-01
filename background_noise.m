clear
close all
cam=webcam(1);
%preview(camera);
for i=1:10
img=snapshot(cam);
%lab=rgb2lab(img);
%ycbcr=rgb2ycbcr(img);

r=img(:,:,1);g=img(:,:,2);b=img(:,:,3);pause(0.01);
img2=snapshot(cam);
r1=img2(:,:,1);g1=img2(:,:,2);b1=img2(:,:,3);
r_dif=abs(r-r1);
g_dif=abs(g-g1);
b_dif=abs(b-b1);
r_final=reshape(r_dif,numel(r_dif),1);
g_final=reshape(g_dif,numel(g_dif),1);
b_final=reshape(b_dif,numel(b_dif),1);
r_Norm = (r_final - min(r_final))/(max(r_final) - min(r_final));
g_Norm = (g_final - min(g_final))/(max(g_final) - min(g_final));
b_Norm = (b_final - min(b_final))/(max(b_final) - min(b_final));
figure(1);subplot(321);plot(r_final,'r');title('Red variance');xlabel('Pixel Value');ylabel('Difference Level in Pixel');
grid on;
subplot(326);plot(g_Norm,'g');title('Green Normalization');xlabel('Pixel Value');ylabel('Difference Level in Pixel');
grid on;
subplot(323);plot(b_final,'b');title('Blue variance');xlabel('Pixel Value');ylabel('Difference Level in Pixel');
grid on;
subplot(322);plot(r_Norm,'r');title('Red Normalization');xlabel('Pixel Value');ylabel('Difference Level in Pixel');
grid on;
subplot(325);plot(g_final,'g');title('Green Variance');xlabel('Pixel Value');ylabel('Difference Level in Pixel');
grid on;
subplot(324);plot(b_Norm,'b');title('Blue Normalization');xlabel('Pixel Value');ylabel('Difference Level in Pixel');
grid on;
drawnow
pause(0.2);
end