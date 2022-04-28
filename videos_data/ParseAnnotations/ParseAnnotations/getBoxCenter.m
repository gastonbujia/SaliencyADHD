function [cx, cy] = getBoxCenter(fbox)
%getBoxCenter Function to calculate the center of a bounding box

x2 = fbox(1);
x1 = fbox(2);
y2 = fbox(3);
y1 = fbox(4);

%create a polygon from x y coordinates
p_shape = polyshape([x1, x2, x2, x1], [y1, y1, y2, y2]);
%find centroid
[cx, cy] = centroid(p_shape); 
end

