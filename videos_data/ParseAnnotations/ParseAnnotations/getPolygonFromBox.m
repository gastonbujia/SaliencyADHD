function [px, py] = getPolygonFromBox(box)
%getPolygonFromBox Function to transform a bounding box into a polygon

x2 = box(1);
x1 = box(2);
y2 = box(3);
y1 = box(4);

%create a polygon from x y coordinates
p_shape = polyshape([x1, x2, x2, x1], [y1, y1, y2, y2]); 
p = p_shape.Vertices;
px = p(:, 1);
py = p(:, 2);
end
