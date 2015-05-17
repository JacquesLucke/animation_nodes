# this is based on some great work by Guy Lateur

import numpy
from mathutils import Vector, Matrix
from numpy.polynomial import Polynomial

identityMatrix = Matrix.Identity(4)
delta = 0.00001

class BezierCurve:
    def __init__(self):
        self.splines = []
        
    @staticmethod
    def fromBlenderCurveData(blenderCurve):
        curve = BezierCurve()
        for blenderSpline in blenderCurve.splines:
            if blenderSpline.type == "BEZIER":
                spline = BezierSpline.fromBlenderSpline(blenderSpline)
                curve.splines.append(spline)
        return curve
            
    def copy(self):
        curve = BezierCurve()
        curve.splines = [spline.copy() for spline in self.splines]
        return curve
        
    def transform(self, matrix = identityMatrix):
        for spline in self.splines:
            spline.transform(matrix)
        
        
class BezierSpline:
    def __init__(self):
        self.points = []
        self.segments = []
        self.isCyclic = False
        
    @staticmethod
    def fromBlenderSpline(blenderSpline):
        spline = BezierSpline()
        spline.isCyclic = blenderSpline.use_cyclic_u
        for blenderPoint in blenderSpline.bezier_points:
            point = BezierPoint.fromBlenderPoint(blenderPoint)
            spline.points.append(point)
        return spline
            
    def copy(self):
        spline = BezierSpline()
        spline.points = [point.copy() for point in self.points]
        spline.isCyclic = self.isCyclic
        return spline
        
    def transform(self, matrix = identityMatrix):
        for point in self.points:
            point.transform(matrix)
        
    def updateSegments(self):
        self.segments = []
        for left, right in zip(self.points[:-1], self.points[1:]):
            self.segments.append(BezierSegment(left, right))
            
        if self.isCyclic:
            self.segments.append(BezierSegment(self.points[-1], self.points[0]))
            
    def getSamples(self, amount):
        samples = []
        for i in range(max(amount - 1, 0)):
            samples.append(self.evaluate(i / (amount - 1)))
        samples.append(self.evaluate(1))
        return samples
        
    def getTangentSamples(self, amount):
        tangents = []
        for i in range(max(amount - 1, 0)):
            tangents.append(self.evaluateTangent(i / (amount - 1)))
        tangents.append(self.evaluateTangent(1))
        return tangents
        
    def evaluate(self, parameter):
        par = min(max(parameter, 0), 0.9999) * len(self.segments)
        return self.segments[int(par)].evaluate(par - int(par))
        
    def evaluateTangent(self, parameter):
        par = min(max(parameter, 0), 0.9999) * len(self.segments)
        return self.segments[int(par)].evaluateTangent(par - int(par))
        
    def calculateLength(self, samplesPerSegment = 5):
        length = 0
        for segment in self.segments:
            length += segment.calculateLength(samplesPerSegment)
        return length  

    def findNearestSampledParameter(self, point, resolution = 50):
        parameters = [i / (resolution - 1) for i in range(resolution)]
        return chooseNearestParameter(self, point, parameters)
        
    def findNearestParameter(self, point):
        parameters = [(i + segment.findNearestParameter(point)) / len(self.segments) for i, segment in enumerate(self.segments)]
        return chooseNearestParameter(self, point, parameters)
        
    def findNearestPointAndTangentOnExtendedSpline(self, point):
        parameter = self.findNearestParameter(point)
        splineProjection = self.evaluate(parameter)
        splineTangent = self.evaluateTangent(parameter)
        possibleProjectionData = [(splineProjection, splineTangent)]
        
        if not self.isCyclic:
            startPoint = self.evaluate(0)
            startTangent = self.evaluateTangent(0)
            startLineProjection = findNearestPointOnLine(startPoint, startTangent, point)
            if (startLineProjection.x - startPoint.x) / startTangent.x <= 0:
                possibleProjectionData.append((startLineProjection, startTangent))
            
            endPoint = self.evaluate(1)
            endTangent = self.evaluateTangent(1)
            endLineProjection = findNearestPointOnLine(endPoint, endTangent, point)
            if (endLineProjection.x - endPoint.x) / endTangent.x >= 0: 
                possibleProjectionData.append((endLineProjection, endTangent))
        
        return min(possibleProjectionData, key = lambda item: (point - item[0]).length_squared)
        
    def calculateSmoothHandles(self, strength = 1):
        points = self.points
        points[0].calculateSmoothHandles(points[0].location, points[1].location, strength)
        points[-1].calculateSmoothHandles(points[-2].location, points[-1].location, strength)
        for before, point, after in zip(points[:-2], points[1:-1], points[2:]):
            point.calculateSmoothHandles(before.location, after.location, strength)
        
    @property
    def hasSegments(self):
        return len(self.segments) > 0
                
        
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
        return c[0] + c[1] * parameter + c[2] * parameter ** 2 + c[3] * parameter ** 3
        
    def evaluateTangent(self, parameter):
        c = self.coeffs
        return c[1] + c[2] * 2 * parameter + c[3] * 3 * parameter ** 2
        
    def calculateLength(self, samples = 5):
        length = 0
        last = self.evaluate(0)
        for i in range(samples - 1):
            parameter = (i + 1) / (samples - 1)
            current = self.evaluate(parameter)
            length += (current - last).length
            last = current
        return length
        
    def findNearestParameter(self, point):
        return chooseNearestParameter(self, point, self.findRootParameters(point))
    
    # http://jazzros.blogspot.be/2011/03/projecting-point-on-bezier-curve.html    
    def findRootParameters(self, point):
        left = self.left
        right = self.right
        
        p0 = left.location - point
        p1 = left.rightHandle - point
        p2 = right.leftHandle - point
        p3 = right.location - point
        
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
        realRoots = [min(max(root.real, 0), 1) for root in roots]

        return realRoots
        
        
class BezierPoint:
    def __init__(self):
        self.location = Vector((0, 0, 0))
        self.leftHandle = Vector((0, 0, 0))
        self.rightHandle = Vector((0, 0, 0))
        
    @staticmethod
    def fromBlenderPoint(blenderPoint):
        point = BezierPoint()
        point.location = blenderPoint.co
        point.leftHandle = blenderPoint.handle_left
        point.rightHandle = blenderPoint.handle_right
        return point
        
    def copy(self):
        point = BezierPoint()
        point.location = self.location.copy()
        point.leftHandle = self.leftHandle.copy()
        point.rightHandle = self.rightHandle.copy()
        return point    

    def transform(self, matrix = identityMatrix):
        self.location = matrix * self.location
        self.leftHandle = matrix * self.leftHandle
        self.rightHandle = matrix * self.rightHandle
          
    # http://www.antigrain.com/research/bezier_interpolation/          
    def calculateSmoothHandles(self, before, after, strength = 1):
        distanceBefore = (self.location - before).length
        distanceAfter = (self.location - after).length
        proportion = distanceBefore / (distanceBefore + distanceAfter)
        handleDirection = (after - before).normalized()
        self.leftHandle = self.location - handleDirection * proportion * strength
        self.rightHandle = self.location + handleDirection * proportion * strength
            
        
        
# utility functions
##############################

def chooseNearestParameter(curveElement, point, parameters):
    sampledData = [(parameter, (point - curveElement.evaluate(parameter)).length_squared) for parameter in parameters]
    return min(sampledData, key = lambda item: item[1])[0]   

def findNearestPointOnLine(linePosition, lineDirection, point):
    lineDirection = lineDirection.normalized()
    dotProduct = lineDirection.dot(point - linePosition)
    return linePosition + (lineDirection * dotProduct)