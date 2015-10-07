import copy
from mathutils import Vector
from . utils import findNearestParameterOnLine

'''
How to use Splines:
- Don't create an instance of the base Spline class. Use PolySpline or BezierSpline instead
- set the isChanged property to False after you edited the spline
- call the update function on the spline before evaluation, projection, ...
- check the isEvaluable after updating the spline. There may be exceptions when you evaluate the spline when it isn't evaluable
- call the ensureUniformConverter function before converting normal parameters to parameters which have the same distances
'''

class Spline:
    def __getattr__(self, name):
        if name == "type": return "BASE_SPLINE"
        if name == "isCyclic": return False
        if name == "isEvaluable": return False
        if name == "isChanged": return True
        if name == "uniformConverter": return None


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

    def getUniformSamples(self, amount, start = 0.0, end = 1.0, resolution = 100):
        self.ensureUniformConverter(resolution)
        parameters = self.toUniformParameters(amount, start, end)
        return [self.evaluate(par) for par in parameters]

    def getUniformTangentSamples(self, amount, start = 0.0, end = 1.0, resolution = 100):
        self.ensureUniformConverter(resolution)
        parameters = self.toUniformParameters(amount, start, end)
        return [self.evaluateTangent(par) for par in parameters]


    def toUniformParameters(self, amount, start = 0.0, end = 1.0):
        return [self.toUniformParameter(par) for par in self.getParameters(amount, start, end)]

    def getParameters(self, amount, start = 0.0, end = 1.0):
        start = min(max(start, 0.0), 1.0)
        end = min(max(end, 0.0), 1.0)

        if amount == 0: return []
        if amount == 1: return [(start + end) / 2]

        if start > end: start, end = end, start
        factor = (end - start) / (amount - 1)
        return [i * factor + start for i in range(amount)]

    # call ensureUniformConverter first
    def toUniformParameter(self, parameter):
        return self.uniformConverter.lookUp(parameter)



    # the resolution may not be needed in every subclass
    def getLength(self, resolution = 50):
        return self.getPartialLength(resolution, 0.0, 1.0)

    def getPartialLength(self, resolution = 50, start = 0.0, end = 1.0):
        if not self.isEvaluable: return 0.0
        samples = self.getSamples(resolution, start, end)
        return self.calculateDistanceSum(samples)

    def calculateDistanceSum(self, vectors):
        distance = 0.0
        for i in range(len(vectors) - 1):
            distance += (vectors[i] - vectors[i+1]).length
        return distance


    # it's enough when a subclass implements 'getProjectedParameters'
    def project(self, coordinates):
        parameters = self.getProjectedParameters(coordinates)
        sampledData = [(par, (coordinates - self.evaluate(par)).length_squared) for par in parameters]
        if len(sampledData) > 0: return min(sampledData, key = lambda item: item[1])[0]
        else: return 0.0
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



    def getTrimmedVersion(self, start, end):
        from . poly_spline import PolySpline

        self.update()
        if not self.isEvaluable: return self.copy()

        trimmedSpline = PolySpline()
        trimmedSpline.appendPoints(self.getSamples(100, start, end))
        return trimmedSpline



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

# Mainly used to get parameters which have the same distance on the spline
class ParameterConverter:
    def __init__(self, parameterList):
        self.parameters = parameterList
        self.length = len(parameterList)

    def lookUp(self, parameter):
        maxIndex = self.length - 1
        p = min(max(parameter * maxIndex, 0), maxIndex)
        before = int(p)
        after = min(before + 1, maxIndex)
        influence = p - before
        return self.parameters[before] * (1 - influence) + self.parameters[after] * influence

    @property
    def resolution(self):
        return self.length - 1
