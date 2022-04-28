function [Frame, ObjectType, Polygon] = getPolygonsFromAnnotation(annoPath)
%getPolygonsFromAnnotation Parses the annotation file and extracts
% information about the frame, object type, and box coordinates
%
%   This function transforms the annotation file information in to a
%   processable format extracting the frame to which the object box
%   corresonds to, the object class and the bounding box. Note the bounding
%   box is in the size of the original video size. In the task the video
%   was set to full screen having larger coordinates.

% cut out only the important information
R = xml2struct(annoPath);
M = string(char(R.Children.Name));
idx_p = M == "image  ";
allFrames = R.Children(idx_p);

% generate list that can be sorted according to frame
Frame = [];% zeros(length(allObjects), 1); %'Frame'
ObjectType = []; % 'ObjectType',
Polygon =  {}; %cell(length(allObjects), 1); % polygon

for iFrame = 1:length(allFrames)
    % get all polygons of current frame
    idxPoly = string(char(allFrames(iFrame).Children.Name)) == "polygon";
    polyInFrame = [allFrames(iFrame).Children(idxPoly).Attributes];
    
    if ~isempty(polyInFrame)
        
        % extract the object type of all polygons of that frame
        idxLabel = string(char(polyInFrame.Name)) == "label   ";
        ObjectType = [ObjectType; string(char(polyInFrame(idxLabel).Value))];
        
        % extract the polygon points
        idxPoints = find(string(char(polyInFrame.Name)) == "points  ");
        for iItem = 1:length(idxPoints)
            Frame  = [Frame; iFrame];
            Polygon = [Polygon; {str2num(char(polyInFrame(idxPoints(iItem)).Value))}];
        end
    end

    % get all boxes of current frame
    idxBox = string(char(allFrames(iFrame).Children.Name)) == "box    ";
    boxInFrame = [allFrames(iFrame).Children(idxBox).Attributes];
    
    if ~isempty(boxInFrame)
        
        % extract the object type
        idxLabel = string(char(boxInFrame.Name)) == "label   ";
        ObjectType = [ObjectType; string(char(boxInFrame(idxLabel).Value))];
        
        % extract box coordinates
        idxCord = find(string(char(boxInFrame.Name)) == "xbr     ");
        curVal = string(char(boxInFrame(idxLabel).Value));
        for iItem = 1:length(idxCord)
            Frame  = [Frame; iFrame];
            boxCord = str2num(char(boxInFrame([idxCord(iItem): idxCord(iItem)+3]).Value));
            if curVal(iItem) == "Face" 
                % return oval around the face
                [bx, by] = getFaceOval([boxCord]);
            else % its text
                [bx, by] = getPolygonFromBox([boxCord]);
            end
            Polygon = [Polygon; {[bx, by]}];
        end
    end
end
end
