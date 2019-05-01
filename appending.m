%appending values
x=[];
y=[];
z=[];
fileID = fopen('atm_data.txt');
if fileID>0
while ~feof(fileID)
line=fgetl(fileID)
val=strsplit(line,',');
%val(1)=char(val(1));
x=[x,str2double(char(val(1)))];
y=[y,str2double(char(val(2)))]
z=[z,str2double(char(val(3)))]
%%plot(x,'-gs','LineWidth',2,'MarkerEdgeColor','k','MarkerFaceColor','k','MarkerSize',5)
%grid on,title('Temperature Vs Time'),xlabel('Time'),ylabel('Temperature')
%pause(0.5);
end
fclose(fileID);
end
