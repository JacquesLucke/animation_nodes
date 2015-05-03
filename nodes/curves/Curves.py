from . import Math
from mathutils import *

import bpy


# utility functions
def IsCurve(blenderObject):
    if blenderObject is None: return False
    if blenderObject.type == 'CURVE': return True
    
    return False
    
def IsBezierCurve(blenderObject):
    if not IsCurve(blenderObject): return False
    
    for spline in blenderObject.data.splines:
        if spline.type != 'BEZIER': return False
    
    return True
    

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
        
        
    def CalcPoint(self, parameter):
        nrSegs = self.nrSegments
        
        segmentIndex = int(nrSegs * parameter)
        if segmentIndex < 0: segmentIndex = 0
        if segmentIndex > (nrSegs - 1): segmentIndex = nrSegs - 1
        
        segmentParameter = nrSegs * parameter - segmentIndex
        if segmentParameter < 0.0: segmentParameter = 0.0
        if segmentParameter > 1.0: segmentParameter = 1.0
        
        return self.segments[segmentIndex].CalcPoint(parameter = segmentParameter)
        
    def CalcDerivative(self, parameter):
        nrSegs = self.nrSegments
        
        segmentIndex = int(nrSegs * parameter)
        if segmentIndex < 0: segmentIndex = 0
        if segmentIndex > (nrSegs - 1): segmentIndex = nrSegs - 1
        
        segmentParameter = nrSegs * parameter - segmentIndex
        if segmentParameter < 0.0: segmentParameter = 0.0
        if segmentParameter > 1.0: segmentParameter = 1.0
        
        return self.segments[segmentIndex].CalcDerivative(parameter = segmentParameter)
        
    
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
        
        
    def CalcSplineIndexAndParameter(self, parameter):
        nrSpl = self.nrSplines
        if nrSpl < 1: return 0, 0.5
        
        if nrSpl < 1:
            splineIndex = 0
            splineParameter = parameter
        else:
            splineIndex = int(nrSpl * parameter)
            if splineIndex < 0: splineIndex = 0
            if splineIndex > (nrSpl - 1): splineIndex = nrSpl - 1

            splineParameter = nrSpl * parameter - splineIndex
            if splineParameter < 0.0: splineParameter = 0.0
            if splineParameter > 1.0: splineParameter = 1.0
            
        return splineIndex, splineParameter
    
    def CalcPoint(self, parameter):
        splineIndex, splineParameter = self.CalcSplineIndexAndParameter(parameter)
            
        spl = self.splines[splineIndex]
        return spl.CalcPoint(splineParameter)
    
    def CalcPointWorld(self, parameter):
        return self.worldMatrix * self.CalcPoint(parameter)
        
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
        
    def CalcDerivative(self, parameter):
        splineIndex, splineParameter = self.CalcSplineIndexAndParameter(parameter)
            
        spl = self.splines[splineIndex]
        return spl.CalcDerivative(splineParameter)
    
    def CalcDerivativeWorld(self, parameter):
        return self.worldMatrix3x3 * self.CalcDerivative(parameter)
        
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
        
        
        
