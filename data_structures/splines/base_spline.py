import copy
from mathutils import Vector
from ... utils.math import findNearestParameterOnLine

class Spline:
    def __getattr__(self, name):
        if name == "type":
            return "BASE_SPLINE"
        if name == "isCyclic":
            return False
        if name == "isEvaluable":
            return True
        if name == "isChanged":
            return True
        if name == "uniformConverter":
            return None
        
        
    def copy(self):
        return copy.deepcopy(self)
        
       
    def transform(self, matrix):
        return self
        
    
    def appendPoint(self, coordinates):
        return None
        
    def getPoints(self):
        return []
        
        
    # call this before evaluating the spline
    def update(self):
        return None
        
        
    def evaluate(self, parameter):
        return Vector((0, 0, 0))
        
        
    def evaluateTangent(self, parameter):
        return Vector((0, 0, 1))
        
        
    def appendPoints(self, points):
        for point in points:
            self.appendPoint(point)
        
        
    def getSamples(self, amount, start = 0.0, end = 1.0):
        parameters = self.getParameters(amount, start, end)
        return [self.evaluate(par) for par in parameters]
        
    def getTangentSamples(self, amount, start = 0.0, end = 1.0):
        parameters = self.getParameters(amount, start, end)
        return [self.evaluateTangent(par) for par in parameters]
        
    def getUniformSamples(self, amount, start = 0.0, end = 1.0):
        parameters = self.toUniformParameters(amount, start, end)
        return [self.evaluate(par) for par in parameters]
        
    def getUniformTangentSamples(self, amount, start = 0.0, end = 1.0):
        parameters = self.toUniformParameters(amount, start, end)
        return [self.evaluateTangent(par) for par in parameters]
        
        
    def toUniformParameters(self, amount, start = 0.0, end = 1.0):
        return [self.toUniformParameter(par) for par in self.getParameters(amount, start, end)]
        
    def getParameters(self, amount, start = 0.0, end = 1.0):
        if start > end: start, end = end, start
        factor = (end - start) / (amount - 1)
        return [i * factor + start for i in range(amount)]
        
    def toUniformParameter(self, parameter):
        return self.uniformConverter.lookUp(parameter)
        
        
    
    # the resolution may not be needed in every subclass
    def getLength(self, resolution = 50):
        if not self.isEvaluable: return 0.0
        samples = self.getSamples(resolution)
        length = 0.0
        for i in range(resolution - 1):
            length += (samples[i] - samples[i+1]).length
        return length
        
        
    # it's enough when a subclass implements 'getProjectedParameters'
    def project(self, coordinates):
        parameters = self.getProjectedParameters(coordinates)
        sampledData = [(par, (coordinates - self.evaluate(par)).length_squared) for par in parameters]       
        return min(sampledData, key = lambda item: item[1])[0]
    def getProjectedParameters(self, coordinates):
        return [i / 100 for i in range(101)]
        
    
    # find the nearest point and tangent on the spline + the straight lines at the end
    def projectExtended(self, coordinates):
        def findNearestPointOnLine(linePosition, lineDirection, point):
            lineDirection = lineDirection.normalized()
            dotProduct = lineDirection.dot(point - linePosition)
            return linePosition + (lineDirection * dotProduct)
            
        parameter = self.project(coordinates)
        splineProjection = self.evaluate(parameter)
        splineTangent = self.evaluateTangent(parameter)
        projectionData = [(splineProjection, splineTangent)]
        
        # TODO: can cause division by zero here
        if not self.isCyclic:
            startPoint = self.evaluate(0)
            startTangent = self.evaluateTangent(0)
            parameter = findNearestParameterOnLine(startPoint, startTangent, coordinates)
            if parameter <= 0:
                startLineProjection = startPoint + parameter * startTangent
                projectionData.append((startLineProjection, startTangent))
            
            endPoint = self.evaluate(1)
            endTangent = self.evaluateTangent(1)
            parameter = findNearestParameterOnLine(endPoint, endTangent, coordinates)
            if parameter >= 0: 
                endLineProjection = endPoint + parameter * endTangent
                projectionData.append((endLineProjection, endTangent))
        
        return min(projectionData, key = lambda item: (coordinates - item[0]).length_squared)
        
        
    def ensureUniformConverter(self, resolution = 100):
        if getattr(self.uniformConverter, "resolution", 0) < resolution:
            self.newUniformConverter(resolution)
       
    def newUniformConverter(self, resolution = 100):
        from . poly_spline import PolySpline
        samples = self.getSamples(resolution)
        
        polySpline = PolySpline()
        polySpline.appendPoints(samples)
        polySpline.update()
        
        uniformPolySpline = PolySpline()
        equalDistanceParameters = polySpline.getEqualDistanceParameters(resolution)
        converter = ParameterConverter(equalDistanceParameters)
        self.uniformConverter = converter
        
        
        
class ParameterConverter:
    def __init__(self, parameterList):
        self.parameters = parameterList
        self.length = len(parameterList)
        
    def lookUp(self, parameter):
        p = min(max(parameter * self.length, 0), self.length - 1)
        before = int(p)
        after = min(before + 1, self.length - 1)
        influence = p - before
        return self.parameters[before] * (1 - influence) + self.parameters[after] * influence
        
    @property
    def resolution(self):
        return self.length - 1