from . import Math
from mathutils import *

import bpy
import numpy


# utility properties & functions
defaultParameter = 0.5
defaultResolutionAnalysis = 128
deltaParameter = 0.001
deltaParameterImaginary = Math.defaultDeltaImaginary

def IsCurve(blenderObject):
    if blenderObject is None: return False
    if blenderObject.type == 'CURVE': return True

    return False

def IsBezierCurve(blenderObject):
    if not IsCurve(blenderObject): return False

    for spline in blenderObject.data.splines:
        if spline.type != 'BEZIER': return False

    return True
    
def ParameterIsZero(parameter):
    return parameter < deltaParameter

def ParameterIsOne(parameter):
    return parameter + deltaParameter > 1.0

def RootsToParameters(roots):
    realRoots = []
    for root in roots:
        realRoot = Math.ComplexToRealFloat(root, deltaImaginary = deltaParameterImaginary)
        if realRoot is None: continue
        
        realRoots.append(realRoot)
    
    rvParameters = []
    doZero = False
    doOne = False
    for realRoot in realRoots:
        if ParameterIsZero(realRoot):
            doZero = True
            continue
        if ParameterIsOne(realRoot):
            doOne = True
            continue
            
        rvParameters.append(realRoot)
        
    if doZero: rvParameters.append(0.0)
    if doOne: rvParameters.append(1.0)
    
    return rvParameters


class BezierPoint:
    @staticmethod
    def FromBlenderBezierPoint(blenderBezierPoint):
        return BezierPoint(blenderBezierPoint.handle_left, blenderBezierPoint.co, blenderBezierPoint.handle_right)


    def __init__(self, handle_left, co, handle_right):
        self.handle_left = handle_left
        self.co = co
        self.handle_right = handle_right


    def Copy(self):
        return BezierPoint(self.handle_left.copy(), self.co.copy(), self.handle_right.copy())

    def Reversed(self):
        return BezierPoint(self.handle_right, self.co, self.handle_left)

    def Reverse(self):
        tmp = self.handle_left
        self.handle_left = self.handle_right
        self.handle_right = tmp


class BezierSegment:
    @staticmethod
    def FromBlenderBezierPoints(blenderBezierPoint1, blenderBezierPoint2):
        bp1 = BezierPoint.FromBlenderBezierPoint(blenderBezierPoint1)
        bp2 = BezierPoint.FromBlenderBezierPoint(blenderBezierPoint2)

        return BezierSegment(bp1, bp2)


    def __init__(self, bezierPoint1, bezierPoint2):
        # bpy.types.BezierSplinePoint
        # ## NOTE/TIP: copy() helps with repeated (intersection) action -- ??
        self.bezierPoint1 = bezierPoint1.Copy()
        self.bezierPoint2 = bezierPoint2.Copy()

        self.ctrlPnt0 = self.bezierPoint1.co
        self.ctrlPnt1 = self.bezierPoint1.handle_right
        self.ctrlPnt2 = self.bezierPoint2.handle_left
        self.ctrlPnt3 = self.bezierPoint2.co

        self.coeff0 = self.ctrlPnt0
        self.coeff1 = self.ctrlPnt0 * (-3.0) + self.ctrlPnt1 * (+3.0)
        self.coeff2 = self.ctrlPnt0 * (+3.0) + self.ctrlPnt1 * (-6.0) + self.ctrlPnt2 * (+3.0)
        self.coeff3 = self.ctrlPnt0 * (-1.0) + self.ctrlPnt1 * (+3.0) + self.ctrlPnt2 * (-3.0) + self.ctrlPnt3


    def Copy(self):
        return BezierSegment(self.bezierPoint1.Copy(), self.bezierPoint2.Copy())

    def Reversed(self):
        return BezierSegment(self.bezierPoint2.Reversed(), self.bezierPoint1.Reversed())

    def Reverse(self):
        # make a copy, otherwise neighboring segment may be affected
        tmp = self.bezierPoint1.Copy()
        self.bezierPoint1 = self.bezierPoint2.Copy()
        self.bezierPoint2 = tmp
        self.bezierPoint1.Reverse()
        self.bezierPoint2.Reverse()


    def CalcPoint(self, parameter = 0.5):
        parameter2 = parameter * parameter
        parameter3 = parameter * parameter2

        rvPoint = self.coeff0 + self.coeff1 * parameter + self.coeff2 * parameter2 + self.coeff3 * parameter3

        return rvPoint

    def CalcDerivative(self, parameter = 0.5):
        parameter2 = parameter * parameter

        rvPoint = self.coeff1 + self.coeff2 * parameter * 2.0 + self.coeff3 * parameter2 * 3.0

        return rvPoint

    # http://jazzros.blogspot.be/2011/03/projecting-point-on-bezier-curve.html
    def CalcProjectionByPoly5(self, point, matrix = Matrix.Identity):
        p0 = (matrix * self.ctrlPnt0) - point
        p1 = (matrix * self.ctrlPnt1) - point
        p2 = (matrix * self.ctrlPnt2) - point
        p3 = (matrix * self.ctrlPnt3) - point
        
        a = p3 + p2 * (-3.0) + p1 * (+3.0) - p0
        b = p2 * (+3.0) + p1 * (-6.0) + p0 * (+3.0)
        c = (p1 - p0) * (+3.0)
        
        q5 = a.dot(a) * 3.0
        q4 = a.dot(b) * 5.0
        q3 = a.dot(c) * 4.0 + b.dot(b) * 2.0
        q2 = b.dot(c) * 3.0 + a.dot(p0) * 3.0
        q1 = c.dot(c) + b.dot(p0) * 2.0
        q0 = c.dot(p0)
        
        rvParameter = 0.0
        rvDistance2 = -1.0
        
        poly = numpy.polynomial.Polynomial([q0, q1, q2, q3, q4, q5], [0.0, 1.0], [0.0, 1.0])
        roots = poly.roots()
        if len(roots) < 1:
            return rvParameter, rvDistance2
        
        parameters = RootsToParameters(roots)
        nrParameters = len(parameters)
        if len(parameters) < 1: return rvParameter, rvDistance2
        
        rvParameter = parameters[0]
        pointOnCurve = matrix * self.CalcPoint(rvParameter)
        rvDistance2 = (pointOnCurve - point).length_squared
        for iParameter in range(1, nrParameters):
            currParameter = parameters[iParameter]
            pointOnCurve = matrix * self.CalcPoint(currParameter)
            currDistance2 = (pointOnCurve - point).length_squared
            if currDistance2 < rvDistance2:
                rvParameter = currParameter
                rvDistance2 = currDistance2
                
        return rvParameter, rvDistance2

    def CalcLength(self, nrSamples = 2):
        nrSamplesFloat = float(nrSamples)
        rvLength = 0.0
        for iSample in range(nrSamples):
            par1 = float(iSample) / nrSamplesFloat
            par2 = float(iSample + 1) / nrSamplesFloat

            point1 = self.CalcPoint(parameter = par1)
            point2 = self.CalcPoint(parameter = par2)
            diff12 = point1 - point2

            rvLength += diff12.magnitude

        return rvLength

    def CalcLengthTransformed(self, nrSamples = 2, matrix = Matrix.Identity):
        nrSamplesFloat = float(nrSamples)
        rvLength = 0.0
        for iSample in range(nrSamples):
            par1 = float(iSample) / nrSamplesFloat
            par2 = float(iSample + 1) / nrSamplesFloat

            point1 = self.CalcPoint(parameter = par1)
            point2 = self.CalcPoint(parameter = par2)
            diff12 = (matrix * point1) - (matrix * point2)

            rvLength += diff12.magnitude

        return rvLength

    #http://en.wikipedia.org/wiki/De_Casteljau's_algorithm
    def CalcSplitPoint(self, parameter = 0.5):
        par1min = 1.0 - parameter

        bez00 = self.ctrlPnt0
        bez01 = self.ctrlPnt1
        bez02 = self.ctrlPnt2
        bez03 = self.ctrlPnt3

        bez10 = bez00 * par1min + bez01 * parameter
        bez11 = bez01 * par1min + bez02 * parameter
        bez12 = bez02 * par1min + bez03 * parameter

        bez20 = bez10 * par1min + bez11 * parameter
        bez21 = bez11 * par1min + bez12 * parameter

        bez30 = bez20 * par1min + bez21 * parameter

        bezPoint1 = BezierPoint(self.bezierPoint1.handle_left, bez00, bez10)
        bezPointNew = BezierPoint(bez20, bez30, bez21)
        bezPoint2 = BezierPoint(bez12, bez03, self.bezierPoint2.handle_right)

        return [bezPoint1, bezPointNew, bezPoint2]



# TODO: remove dependence on blenderBezierSpline/self.bezierSpline
# TODO: remove bez-segments from definition, as blender splines don't have them (only bez-points)
# ----- -- could still be useful in other calculations, though..
class BezierSpline:
    def __init__(self, blenderBezierSpline):
        self.blenderBezierSpline = blenderBezierSpline

        bezPoints = []

        nrBezPoints = len(blenderBezierSpline.bezier_points)
        for iBezierPoint in range(nrBezPoints):
            bezPoints.append(BezierPoint.FromBlenderBezierPoint(blenderBezierSpline.bezier_points[iBezierPoint]))

        self.bezierPoints = []
        for ip in range(len(bezPoints)): self.bezierPoints.append(bezPoints[ip])

    def __getattr__(self, attrName):
        if attrName == "blenderResolution":
            return self.blenderBezierSpline.resolution_u

        if attrName == "isCyclic":
            return self.blenderBezierSpline.use_cyclic_u

        if attrName == "nrBezierPoints":
            return len(self.bezierPoints)

        if attrName == "segments":
            rvSegments = []

            for iBezierPoint in range(self.nrBezierPoints - 1):
                bezierPoint1 = self.bezierPoints[iBezierPoint]
                bezierPoint2 = self.bezierPoints[iBezierPoint + 1]
                rvSegments.append(BezierSegment.FromBlenderBezierPoints(bezierPoint1, bezierPoint2))

            if self.isCyclic:
                bezierPoint1 = self.bezierPoints[-1]
                bezierPoint2 = self.bezierPoints[0]
                rvSegments.append(BezierSegment.FromBlenderBezierPoints(bezierPoint1, bezierPoint2))

            return rvSegments

        if attrName == "nrSegments":
            return len(self.segments)

        if attrName == "resolution":
            return (self.nrSegments + 1)

        if attrName == "length":
            return self.CalcLength(self.resolution)

        return None

        
    def CalcSegmentIndexAndParameter(self, splineParameter):
        nrSegments = self.nrSegments

        segmentIndex = int(nrSegments * splineParameter)
        if segmentIndex < 0: segmentIndex = 0
        if segmentIndex > (nrSegments - 1): segmentIndex = nrSegments - 1

        segmentParameter = nrSegments * splineParameter - segmentIndex
        if segmentParameter < 0.0: segmentParameter = 0.0
        if segmentParameter > 1.0: segmentParameter = 1.0
        
        return segmentIndex, segmentParameter

    def CalcParameter(self, segmentIndex, segmentParameter):
        try: return (segmentParameter + float(segmentIndex)) / float(self.nrSegments)
        except: return defaultParameter

    def CalcPointOnSegment(self, segmentIndex, segmentParameter):
        try: return self.segments[segmentIndex].CalcPoint(segmentParameter)
        except: return None

    def CalcDerivativeOnSegment(self, segmentIndex, segmentParameter):
        try: return self.segments[segmentIndex].CalcDerivative(segmentParameter)
        except: return None

        
    def CalcPoint(self, parameter):
        segmentIndex, segmentParameter = self.CalcSegmentIndexAndParameter(parameter)

        return self.CalcPointOnSegment(segmentIndex, segmentParameter)
        
    def CalcDerivative(self, parameter):
        segmentIndex, segmentParameter = self.CalcSegmentIndexAndParameter(parameter)

        return self.CalcDerivativeOnSegment(segmentIndex, segmentParameter)

    def CalcProjectionByPoly5(self, point, matrix = Matrix.Identity):
        rvSegmentIndex = 0
        rvSegmentParameter = defaultParameter
        rvDistance2 = -1.0
        
        segments = self.segments
        nrSegments = len(segments)
        if nrSegments < 1: return rvSegmentIndex, rvSegmentParameter, rvDistance2
        
        segment = segments[rvSegmentIndex]
        rvSegmentParameter, rvDistance2 = segment.CalcProjectionByPoly5(point, matrix)
        for iSegment in range(1, nrSegments):
            segment = segments[iSegment]
            currSegmentParameter, currDistance2 = segment.CalcProjectionByPoly5(point, matrix)
            
            if rvDistance2 < 0.0:
                rvSegmentIndex = iSegment
                rvSegmentParameter = currSegmentParameter
                rvDistance2 = currDistance2
                continue
                
            if currDistance2 < rvDistance2:
                rvSegmentIndex = iSegment
                rvSegmentParameter = currSegmentParameter
                rvDistance2 = currDistance2
                
        return rvSegmentIndex, rvSegmentParameter, rvDistance2

        
    def CalcLength(self, resolution):
        try: nrSamplesPerSegment = int(resolution / self.nrSegments)
        except: nrSamplesPerSegment = 2
        if nrSamplesPerSegment < 2: nrSamplesPerSegment = 2

        rvLength = 0.0
        for segment in self.segments:
            rvLength += segment.CalcLength(nrSamples = nrSamplesPerSegment)

        return rvLength

    def CalcLengthTransformed(self, resolution, matrix):
        try: nrSamplesPerSegment = int(resolution / self.nrSegments)
        except: nrSamplesPerSegment = 2
        if nrSamplesPerSegment < 2: nrSamplesPerSegment = 2

        rvLength = 0.0
        for segment in self.segments:
            rvLength += segment.CalcLengthTransformed(nrSamplesPerSegment, matrix)

        return rvLength

    def CalcLengthWithBlenderResolution(self):
        return self.CalcLength(self.blenderResolution)

    def CalcLengthTransformedWithBlenderResolution(self, matrix):
        return self.CalcLengthTransformed(self.blenderResolution, matrix)



# TODO: Curve
class Curve:
    def __init__(self, blenderCurve):
        self.curve = blenderCurve
        self.curveData = blenderCurve.data

        self.splines = self.SetupSplines()

    def SetupSplines(self):
        rvSplines = []
        for spline in self.curveData.splines:
            if spline.type != 'BEZIER':
                print("## WARNING: only bezier splines are supported, atm; other types are ignored")
                continue

            try: newSpline = BezierSpline(spline)
            except:
                print("## EXCEPTION: newSpline = BezierSpline.FromBlenderBezierSpline(spline)")
                continue

            rvSplines.append(newSpline)

        return rvSplines

    def __getattr__(self, attrName):
        if attrName == "nrSplines":
            return len(self.splines)

        if attrName == "blenderNrSplines":
            return len(self.curveData.splines)

        if attrName == "blenderSplineTypes":
            rvTypes = []

            for spline in self.curveData.splines: rvTypes.append(spline.type)

            return rvTypes


        if attrName == "length":
            return self.CalcLength()

        if attrName == "lengthWorld":
            return self.CalcLengthWorld()

        if attrName == "worldMatrix":
            return self.curve.matrix_world

        if attrName == "worldMatrix3x3":
            return self.worldMatrix.to_3x3()

        if attrName == "location":
            return self.curve.location

        return None


    def RebuildInScene(self):
        self.curveData.splines.clear()

        for spline in self.splines:
            blSpline = self.curveData.splines.new('BEZIER')
            blSpline.use_cyclic_u = spline.isCyclic
            blSpline.resolution_u = spline.resolution

            bezierPoints = []
            for segment in spline.segments: bezierPoints.append(segment.bezierPoint1)
            if not spline.isCyclic: bezierPoints.append(spline.segments[-1].bezierPoint2)
            #else: print("????", "spline.isCyclic")

            nrBezierPoints = len(bezierPoints)
            blSpline.bezier_points.add(nrBezierPoints - 1)

            for i, blBezPoint in enumerate(blSpline.bezier_points):
                bezPoint = bezierPoints[i]

                blBezPoint.tilt = 0
                blBezPoint.radius = 1.0

                blBezPoint.handle_left_type = 'FREE'
                blBezPoint.handle_left = bezPoint.handle_left
                blBezPoint.co = bezPoint.co
                blBezPoint.handle_right_type = 'FREE'
                blBezPoint.handle_right = bezPoint.handle_right


    def CalcSplineIndexAndParameter(self, curveParameter):
        nrSpl = self.nrSplines
        if nrSpl < 1: return 0, 0.5

        if nrSpl is 1:
            splineIndex = 0
            splineParameter = curveParameter
        else:
            splineIndex = int(nrSpl * curveParameter)
            if splineIndex < 0: splineIndex = 0
            if splineIndex > (nrSpl - 1): splineIndex = nrSpl - 1

            splineParameter = nrSpl * curveParameter - splineIndex
            if splineParameter < 0.0: splineParameter = 0.0
            if splineParameter > 1.0: splineParameter = 1.0

        return splineIndex, splineParameter

    def CalcParameter(self, splineIndex, splineParameter):
        try: return (splineParameter + float(splineIndex)) / float(self.nrSplines)
        except: return defaultParameter

        
    def CalcPointOnSpline(self, splineIndex, splineParameter):
        try: return self.splines[splineIndex].CalcPoint(splineParameter)
        except: return None

    def CalcPointOnSplineWorld(self, splineIndex, splineParameter):
        pointOnSpline = self.CalcPointOnSpline(splineIndex, splineParameter)
        if pointOnSpline is None: return None
        
        return self.worldMatrix * pointOnSpline
    
    def CalcPoint(self, parameter):
        splineIndex, splineParameter = self.CalcSplineIndexAndParameter(parameter)

        return self.CalcPointOnSpline(splineIndex, splineParameter)

    def CalcPointWorld(self, parameter):
        splineIndex, splineParameter = self.CalcSplineIndexAndParameter(parameter)

        return self.CalcPointOnSplineWorld(splineIndex, splineParameter)
        
    def Sample(self, resolution):
        rvList = []

        fltResolutionM1 = float(resolution - 1)
        for iSample in range(resolution):
            par = float(iSample) / fltResolutionM1
            rvList.append(self.CalcPoint(par))

        return rvList

    def SampleWorld(self, resolution):
        rvList = []

        fltResolutionM1 = float(resolution - 1)
        for iSample in range(resolution):
            par = float(iSample) / fltResolutionM1
            rvList.append(self.CalcPointWorld(par))

        return rvList

        
    def CalcDerivativeOnSpline(self, splineIndex, splineParameter):
        try: return self.splines[splineIndex].CalcDerivative(splineParameter)
        except: return None

    def CalcDerivativeOnSplineWorld(self, splineIndex, splineParameter):
        derivativeOnSpline = self.CalcDerivativeOnSpline(splineIndex, splineParameter)
        if derivativeOnSpline is None: return None
        
        return self.worldMatrix3x3 * derivativeOnSpline

    def CalcDerivative(self, parameter):
        splineIndex, splineParameter = self.CalcSplineIndexAndParameter(parameter)

        return self.CalcDerivativeOnSpline(splineIndex, splineParameter)

    def CalcDerivativeWorld(self, parameter):
        splineIndex, splineParameter = self.CalcSplineIndexAndParameter(parameter)

        return self.CalcDerivativeOnSplineWorld(splineIndex, splineParameter)

    def SampleDerivatives(self, resolution):
        rvList = []

        fltResolutionM1 = float(resolution - 1)
        for iSample in range(resolution):
            par = float(iSample) / fltResolutionM1
            rvList.append(self.CalcDerivative(par))

        return rvList

    def SampleDerivativesWorld(self, resolution):
        rvList = []
        wm3x3 = self.worldMatrix3x3

        fltResolutionM1 = float(resolution - 1)
        for iSample in range(resolution):
            par = float(iSample) / fltResolutionM1
            rvList.append(wm3x3 * self.CalcDerivative(par))

        return rvList


    def CalcProjection(self, point, resolution):
        samplesWorld = self.SampleWorld(resolution)
        deltaParameter = float(1.0 / float(resolution - 1))

        rvParameter = 0.0
        rvLength2 = (samplesWorld[0] - point).length_squared
        for iSample in range(1, resolution):
            currParameter = deltaParameter * float(iSample)
            currLength2 = (samplesWorld[iSample] - point).length_squared
            if currLength2 < rvLength2:
                rvLength2 = currLength2
                rvParameter = currParameter
                
        return rvParameter

    def CalcProjectionByPoly5(self, point):
        rvSplineIndex = 0
        rvSplineParameter = defaultParameter
        rvDistance2 = -1.0
        
        nrSplines = self.nrSplines
        if nrSplines < 1: return rvSplineIndex, rvSplineParameter, rvDistance2
        
        worldMatrix = self.worldMatrix
        spline = self.splines[rvSplineIndex]
        currSegmentIndex, currSegmentParameter, currDistance2 = spline.CalcProjectionByPoly5(point, worldMatrix)
        rvSplineParameter = spline.CalcParameter(currSegmentIndex, currSegmentParameter)
        rvDistance2 = currDistance2
        for iSpline in range(1, nrSplines):
            spline = self.splines[iSpline]
            currSegmentIndex, currSegmentParameter, currDistance2 = spline.CalcProjectionByPoly5(point, worldMatrix)
            
            if rvDistance2 < 0.0:
                rvSplineIndex = iSpline
                rvSplineParameter = spline.CalcParameter(currSegmentIndex, currSegmentParameter)
                rvDistance2 = currDistance2
                continue
                
            if currDistance2 < rvDistance2:
                rvSplineIndex = iSpline
                rvSplineParameter = spline.CalcParameter(currSegmentIndex, currSegmentParameter)
                rvDistance2 = currDistance2
                
        return rvSplineIndex, rvSplineParameter, rvDistance2
        

    def CalcLength(self):
        rvLength = 0.0
        for spline in self.splines:
            rvLength += spline.length

        return rvLength

    def CalcLengthWorld(self):
        rvLength = 0.0
        for spline in self.splines:
            rvLength += spline.CalcLengthTransformed(spline.resolution, self.worldMatrix)

        return rvLength

    def CalcLengthWithBlenderResolution(self):
        rvLength = 0.0
        for spline in self.splines:
            rvLength += spline.CalcLengthWithBlenderResolution()

        return rvLength

    def CalcLengthWorldWithBlenderResolution(self):
        rvLength = 0.0
        for spline in self.splines:
            rvLength += spline.CalcLengthTransformedWithBlenderResolution(self.worldMatrix)

        return rvLength


