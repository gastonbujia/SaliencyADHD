% Script to read annotations as they come from CVAT and extend all polygons
% to accomodate for eye tracker inaccuracies by maximum radius of EXT.

addpath('toolboxes')

% 0. setup paths
dataPath = '..';
annoPath = [dataPath '/annotationsTP.xml'];

% 2. parse annotations XML
[Frame, ObjectType, Polygon] = getPolygonsFromAnnotation(annoPath);
tosave = array2table([Frame, ObjectType]);
writetable(tosave, 'annotationsTP.csv')
