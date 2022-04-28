function [px, py] = getFaceOval(faceBox)
%getFaceOval Extracts the bounding box of the face and returns an oval
%centered at the face

[cx, cy] = getBoxCenter(faceBox);

wx = faceBox(1)-faceBox(2);
wy = faceBox(1)-faceBox(2);

baseFacePoly = nsidedpoly(20, 'Center', [cx cy], 'Radius', wx/2);
scaledFacePoly = scale(baseFacePoly, [1 wy/wx] ,[cx cy]);

px = scaledFacePoly.Vertices(:, 1);
py = scaledFacePoly.Vertices(:, 2);

end

