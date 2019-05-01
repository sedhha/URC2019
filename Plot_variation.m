function createfigure(yvector1)
%CREATEFIGURE(yvector1)
%  YVECTOR1:  bar yvector

%  Auto-generated by MATLAB on 19-Mar-2019 00:26:30

% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create bar
bar(yvector1,'DisplayName','Red Variance');

% Create xlabel
xlabel('Pixel Number');

% Create title
title('Red Variance');

box(axes1,'on');
% Set the remaining axes properties
set(axes1,'Color',[0.831372559070587 0.815686285495758 0.7843137383461],...
    'XColor',[0 0 0],'XGrid','on','YColor',[0 0 0],'YGrid','on','ZColor',...
    [0 0 0]);