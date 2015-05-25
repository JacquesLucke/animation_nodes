import numpy
from mathutils import Vector, Matrix
from numpy.polynomial import Polynomial
from . base_spline import Spline


class BezierSpline(Spline):
    def __init__(self):
        self.type = "BEZIER"
        self.points = []
        self.isCyclic = False
        self.segments = []
        
    @staticmethod
    def fromLocations(locations):
        spline = BezierSpline()
        for location in locations:
            point = BezierPoint(location, location.copy(), location.copy())
            spline.points.append(point)
        return spline
        
    def copy(self):
        spline = BezierSpline()
        spline.isCyclic = self.isCyclic
        spline.points = [point.copy() for point in self.points]
        return spline
        
    def transform(self, matrix):
        for point in self.points:
            point.transform(matrix)
            
    def appendPoint(self, coordinates):
        self.appendBezierPoint(coordinates, coordinates.copy(), coordinates.copy())
        
    def getPoints(self):
        return [point.location for point in self.points]
        
    def appendBezierPoint(self, location, leftHandle, rightHandle):
        point = BezierPoint(location, leftHandle, rightHandle)
        self.points.append(point)
        
    def update(self):
        def recreateSegments():
            self.segments = []
            for left, right in zip(self.points[:-1], self.points[1:]):
                self.segments.append(BezierSegment(left, right))
            if self.isCyclic:
                self.segments.append(BezierSegment(self.points[-1], self.points[0]))
                
        recreateSegments()
        self.isEvaluable = len(self.segments) > 0
        
    def getProjectedParameters(self, coordinates):
        parameters = []
        for i, segment in enumerate(self.segments):
            for parameter in segment.findRootParameters(coordinates):
                parameters.append((parameter + i) / len(self.segments))
        return parameters
        
    def calculateSmoothHandles(self, strength = 0.3333):
        neighborSegments = self.getNeighborSegments()
        for segment in neighborSegments:
            segment.calculateSmoothHandles(strength)
            
    def getNeighborSegments(self):
        points = self.points
        if len(points) < 2: return []
        neighborSegments = []
        if self.isCyclic:
            for i, point in enumerate(points):
                segment = BezierNeighbors(points[i-2].location, points[i-1], point.location)
                neighborSegments.append(segment)
        else:
            neighborSegments.append(BezierNeighbors(points[0].location, points[0], points[1].location))
            neighborSegments.append(BezierNeighbors(points[-2].location, points[-1], points[-1].location))
            for before, point, after in zip(points[:-2], points[1:-1], points[2:]):
                neighborSegments.append(BezierNeighbors(before.location, point, after.location))
        return neighborSegments
        
    # evaluation
    #############################    
    
    def evaluate(self, parameter):
        par = self.toSegmentsParameter(parameter)
        return self.segments[int(par)].evaluate(par - int(par))
        
    def evaluateTangent(self, parameter):
        par = self.toSegmentsParameter(parameter)
        return self.segments[int(par)].evaluateTangent(par - int(par))
        
    def toSegmentsParameter(self, parameter):
        return min(max(parameter, 0), 0.9999) * len(self.segments)
        
    
class BezierPoint:
    def __init__(self, location, leftHandle, rightHandle):
        self.location = location
        self.leftHandle = leftHandle
        self.rightHandle = rightHandle
        
    def copy(self):
        return BezierPoint(self.location.copy(), self.leftHandle.copy(), self.rightHandle.copy())
        
    def transform(self, matrix):
        self.location = matrix * self.location
        self.leftHandle = matrix * self.leftHandle
        self.rightHandle = matrix * self.rightHandle
        
        
class BezierSegment:
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
        self.coeffs = [
            left.location,
            left.location * (-3.0) + left.rightHandle * (+3.0),
            left.location * (+3.0) + left.rightHandle * (-6.0) + right.leftHandle * (+3.0),
            left.location * (-1.0) + left.rightHandle * (+3.0) + right.leftHandle * (-3.0) + right.location]
            
    def evaluate(self, parameter):
        c = self.coeffs
        return c[0] + parameter * (c[1] + parameter * (c[2] + parameter * c[3]))
        
    def evaluateTangent(self, parameter):
        c = self.coeffs
        return c[1] + parameter * (c[2] * 2 + parameter * c[3] * 3)
        
    # http://jazzros.blogspot.be/2011/03/projecting-point-on-bezier-curve.html   
    # calculate possible parameters which can be the closest to a given point
    def findRootParameters(self, coordinates):
        left = self.left
        right = self.right
        
        p0 = left.location - coordinates
        p1 = left.rightHandle - coordinates
        p2 = right.leftHandle - coordinates
        p3 = right.location - coordinates
        
        a = p3 - 3 * p2 + 3 * p1 - p0
        b = 3 * p2 - 6 * p1 + 3 * p0
        c = 3 * (p1 - p0)
        
        coeffs = [0] * 6
        coeffs[0] = c.dot(p0)
        coeffs[1] = c.dot(c) + b.dot(p0) * 2.0
        coeffs[2] = b.dot(c) * 3.0 + a.dot(p0) * 3.0
        coeffs[3] = a.dot(c) * 4.0 + b.dot(b) * 2.0
        coeffs[4] = a.dot(b) * 5.0
        coeffs[5] = a.dot(a) * 3.0
        
        poly = Polynomial(coeffs, [0.0, 1.0], [0.0, 1.0])
        roots = poly.roots()
        realRoots = [float(min(max(root.real, 0), 1)) for root in roots]

        return realRoots 
        
        
class BezierNeighbors:                
    def __init__(self, leftLocation, point, rightLocation):
        self.point = point
        self.leftLocation = leftLocation
        self.rightLocation = rightLocation
        
    # http://stackoverflow.com/questions/13037606/how-does-inkscape-calculate-the-coordinates-for-control-points-for-smooth-edges/13425159#13425159
    def calculateSmoothHandles(self, strength = 0.3333):
        vecLeft = self.leftLocation - self.point.location
        vecRight = self.rightLocation - self.point.location
        
        lenLeft = vecLeft.length
        lenRight = vecRight.length
        
        if lenLeft > 0 and lenRight > 0:
            dir = ((lenLeft / lenRight) * vecRight - vecLeft).normalized()
            
            self.point.leftHandle = self.point.location - dir * lenLeft * strength
            self.point.rightHandle = self.point.location + dir * lenRight * strength
            
    # http://www.antigrain.com/research/bezier_interpolation/          
    def calculateSmoothHandlesOLD(self, strength = 1):
        co = self.point.location
        distanceBefore = (co - self.leftLocation).length
        distanceAfter = (co - self.rightLocation).length
        proportion = distanceBefore / max(distanceBefore + distanceAfter, 0.00001)
        handleDirection = (self.rightLocation - self.leftLocation).normalized()
        self.point.leftHandle = co - handleDirection * proportion * strength
        self.point.rightHandle = co + handleDirection * proportion * strength 