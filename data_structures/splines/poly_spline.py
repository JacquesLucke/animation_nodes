from . base_spline import Spline


class PolySpline(Spline):
    def __init__(self):
        self.type = "POLY"
        self.points = []
        self.isCyclic = False
        self.segments = []
        self.segmentAmount = 0
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
            self.segmentAmount = len(self.segments)
             
        if self.isChanged:
            recreateSegments()
            self.isEvaluable = len(self.segments) > 0
            self.uniformParameterConverter = None
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
        index, p = self.toSegmentsIndexAndParameter(parameter)
        return self.segments[index].evaluate(p)
        
    def evaluateTangent(self, parameter):
        index, p = self.toSegmentsIndexAndParameter(parameter)
        return self.segments[index].tangent
        
    def toSegmentsIndexAndParameter(self, parameter):
        p = max(parameter, 0.0) * self.segmentAmount
        floorP = int(p)
        if floorP < self.segmentAmount: 
            return floorP, p - floorP
        else:
            return self.segmentAmount - 1, 1
        
        
    # point distribution
    #############################
    
    def getEqualDistanceParameters(self, amount):
        if amount < 2: return [0.0]
        if not self.isEvaluable: return [0.0]

        totalLength = self.getLength()
        distancePerStep = totalLength / amount
        
        parameters = [0.0]
        lastControlPoint = self.points[0]
        lastVector = self.points[0]
        previousDistance = 0.0
        
        targetPoints = self.points[1:]
        targetPointAmount = len(targetPoints)
        
        for i, point in enumerate(targetPoints):
            while True:
                distanceToLastVector = (point - lastVector).length
                totalDistance = distanceToLastVector + previousDistance
                
                if totalDistance >= distancePerStep:
                    # find vector with correct distance
                    surplusDistance = totalDistance - distancePerStep    
                    influence = surplusDistance / distanceToLastVector
                    sampledVector = lastVector * influence + point * (1 - influence)
                    
                    # calculate parameter of the sampled vector
                    d1 = (sampledVector - lastControlPoint).length
                    d2 = (point - lastControlPoint).length
                    parameter = (i + d1 / d2) / targetPointAmount
                    parameters.append(parameter)
                    
                    previousDistance = 0.0
                    lastVector = sampledVector
                else:
                    previousDistance += distanceToLastVector
                    lastVector = point
                    break
            lastControlPoint = point
                
        # append parameter 1.0 sometimes because of math inaccuracy
        if parameters[-1] < 0.999999:
            parameters.append(1.0)
        return parameters
        
        
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