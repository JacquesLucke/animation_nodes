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
        
    @staticmethod
    def fromLocations(locations):
        spline = BezierSpline()
        for location in locations:
            spline.points.append(BezierPoint.fromLocation(location))
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
            
    # another algorithm is possibly better
    # and a method to calculate a given number of equally spaced vectors is needed
    # http://math.stackexchange.com/questions/321293/find-coordinates-of-equidistant-points-in-bezier-curve
    def getEqualDistanceSamples(self, distance, resolution = 100):
        distance = distance ** 2
        samples = self.getSamples(resolution)
        points = [samples[0]]
        for i, sample in enumerate(samples[1:]):
            distanceToLastSample = (sample - points[-1]).length_squared
            if distanceToLastSample > distance:
                lastDistanceToLastSample = (points[-1] - samples[i - 1]).length_squared
                d1 = distance - lastDistanceToLastSample
                d2 = distanceToLastSample - distance
                influence = d1 / (d1 + d2)
                points.append(sample * influence + samples[i - 1] * (1 - influence))
        return points
            
    def getSamples(self, amount):
        return self.sampleFunction(self.evaluate, amount)
        
    def getTangentSamples(self, amount):
        return self.sampleFunction(self.evaluateTangent, amount)
        
    def getLinearSamples(self, amount):
        return self.sampleFunction(self.evaluateLinear, amount)
        
    def sampleFunction(self, function, amount):
        samples = []
        for i in range(max(amount - 1, 0)):
            samples.append(function(i / (amount - 1)))
        samples.append(function(1))
        return samples
        
    def evaluate(self, parameter):
        par = self.toSegmentsParameter(parameter)
        return self.segments[int(par)].evaluate(par - int(par))
        
    def evaluateTangent(self, parameter):
        par = self.toSegmentsParameter(parameter)
        return self.segments[int(par)].evaluateTangent(par - int(par))
        
    def evaluateLinear(self, parameter):
        par = self.toSegmentsParameter(parameter)
        return self.segments[int(par)].evaluateLinear(par - int(par))
        
    def toSegmentsParameter(self, parameter):
        return min(max(parameter, 0), 0.9999) * len(self.segments)
        
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
        interpolationSegments = self.getInterpolationSegments()
                
        for segment in interpolationSegments:
            segment.calculateSmoothHandles(strength)
            
    def getInterpolationSegments(self):
        points = self.points
        interpolationSegments = []
        if self.isCyclic:
            for i, point in enumerate(points):
                segment = BezierNeighbors(points[i-2].location, points[i-1], point.location)
                interpolationSegments.append(segment)
        else:
            interpolationSegments.append(BezierNeighbors(points[0].location, points[0], points[1].location))
            interpolationSegments.append(BezierNeighbors(points[-2].location, points[-1], points[-1].location))
            for before, point, after in zip(points[:-2], points[1:-1], points[2:]):
                interpolationSegments.append(BezierNeighbors(before.location, point, after.location))
        return interpolationSegments
        
    @property
    def hasSegments(self):
        return len(self.segments) > 0
                
                                
class BezierNeighbors:                
    def __init__(self, leftLocation, point, rightLocation):
        self.point = point
        self.leftLocation = leftLocation
        self.rightLocation = rightLocation
        
    # http://www.antigrain.com/research/bezier_interpolation/          
    def calculateSmoothHandles(self, strength = 1):
        co = self.point.location
        distanceBefore = (co - self.leftLocation).length
        distanceAfter = (co - self.rightLocation).length
        proportion = distanceBefore / (distanceBefore + distanceAfter)
        handleDirection = (self.rightLocation - self.leftLocation).normalized()
        self.point.leftHandle = co - handleDirection * proportion * strength
        self.point.rightHandle = co + handleDirection * proportion * strength
        
        
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
        
    def evaluateLinear(self, parameter):
        return self.left.location * (1 - parameter) + self.right.location * parameter
        
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
        
    @staticmethod
    def fromLocation(location):
        point = BezierPoint()
        point.location = location
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
            
        
        
# utility functions
##############################

def chooseNearestParameter(curveElement, point, parameters):
    sampledData = [(parameter, (point - curveElement.evaluate(parameter)).length_squared) for parameter in parameters]
    return min(sampledData, key = lambda item: item[1])[0]   

def findNearestPointOnLine(linePosition, lineDirection, point):
    lineDirection = lineDirection.normalized()
    dotProduct = lineDirection.dot(point - linePosition)
    return linePosition + (lineDirection * dotProduct)