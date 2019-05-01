%% Martian Geology
%% Rock Size
image=imread('Mars_geology2.jpg');
imagegray=rgb2gray(image);
subplot(331),imcontour(imagegray,5),title('Filter=5');
subplot(332),imcontour(imagegray,10),title('Filter=10');
subplot(333),imcontour(imagegray,15),title('Filter=15');
subplot(334),imcontour(imagegray,20),title('Filter=20');
subplot(335),imcontour(imagegray,25),title('Filter=25');
subplot(336),imcontour(imagegray,30),title('Filter=30');
subplot(337),imcontour(imagegray,35),title('Filter=35');
subplot(338),imcontour(imagegray,40),title('Filter=40');
subplot(339),imcontour(imagegray,45),title('Filter=45');