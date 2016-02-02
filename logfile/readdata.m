clear;
addpath('./bolt_with_nms/')
i=15;
data=importdata(sprintf('%d_0175',i));


shapeInserter = vision.ShapeInserter;
shapeInserter.LineWidth = 1;
shapeInserter.BorderColor = 'White';
bool = data(:,5)>0.2;
data=int32(data);

data=data(bool,1:4);
size(data,1)
data(:,3:4) = data(:,3:4)-data(:,1:2);
I = imread('~/Desktop/imtracking/img/bolt/0175.jpg');
J = step(shapeInserter, I, data);
imshow(J);