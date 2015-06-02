from . base_spline import Spline


class PolySpline(Spline):
    def __init__(self):
        self.type = "POLY"
        self.points = []
        self.isCyclic = False
        self.segments = []
        self.isChanged = True
        
    @staticmethod
    def fromLocations(locations):
        spline = PolySpline()
        spline.points = locations
        return spline
        
    def copy(self):
        spline = PolySpline()
        spline.isCyclic = self.isCyclic
        spline.points = [point.copy() for point in self.points]
        return spline
    
    def transform(self, matrix):
        newPoints = []
        for point in self.points:
            newPoints.append(matrix * point)
        self.points = newPoints
        
    def appendPoints(self, points):
        self.points.extend(points)
            
    def appendPoint(self, coordinates):
        self.points.append(coordinates)
        
    def getPoints(self):
        return self.points
        
    def update(self):
        def recreateSegments():
            self.segments = []
            if len(self.points) < 2: return
            for left, right in zip(self.points[:-1], self.points[1:]):
                self.segments.append(PolySegment(left, right))
            if self.isCyclic:
                self.segments.append(PolySegment(self.points[-1], self.points[0]))
             
        if self.isChanged:
            recreateSegments()
            self.isEvaluable = len(self.segments) > 0
            self.isChanged = False
        
    def getLength(self, resolution = 0):
        length = 0
        for segment in self.segments:
            length += segment.getLength()
        return length
        
    def getProjectedParameters(self, coordinates):
        parameters = []
        for i, segment in enumerate(self.segments):
            parameter = segment.project(coordinates)
            parameters.append((parameter + i) / len(self.segments))
        return parameters
        
        
    # evaluation
    #############################    
    
    def evaluate(self, parameter):
        par = self.toSegmentsParameter(parameter)
        return self.segments[int(par)].evaluate(par - int(par))
        
    def evaluateTangent(self, parameter):
        par = self.toSegmentsParameter(parameter)
        return self.segments[int(par)].tangent
        
    def toSegmentsParameter(self, parameter):
        return min(max(parameter, 0), 0.9999) * len(self.segments)
        
        
class PolySegment:
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.tangent = self.right - self.left
        
    def evaluate(self, parameter):
        return self.left * (1 - parameter) + self.right * parameter
        
    def getLength(self):
        return (self.left - self.right).length
        
    def project(self, coordinates):
        return findNearestParameterOnLine(self.left, self.tangent, coordinates)

def findNearestParameterOnLine(linePosition, lineDirection, point):
    directionLength = lineDirection.length
    lineDirection = lineDirection.normalized()
    parameter = (lineDirection.dot(point - linePosition)) / directionLength
    return parameter    