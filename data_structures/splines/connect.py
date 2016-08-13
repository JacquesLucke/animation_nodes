from . poly_spline import PolySpline
from . bezier_spline import BezierSpline

def connectSplines(list splines):
    if len(splines) == 0: return BezierSpline()
    if len(splines) == 1: return splines[0].copy()

    if allPolySplines(splines):
        return joinPolySplines(splines)
    else:
        return joinInBezierSpline(splines)

def joinPolySplines(splines):
    newSpline = PolySpline()
    for spline in splines:
        newSpline.points.extend(spline.points)
    return newSpline

def joinInBezierSpline(splines):
    newSpline = BezierSpline()
    for spline in splines:
        newSpline.points.extend(spline.points)
        if isinstance(spline, PolySpline):
            newSpline.leftHandles.extend(spline.points)
            newSpline.rightHandles.extend(spline.points)
        elif isinstance(spline, BezierSpline):
            newSpline.leftHandles.extend(spline.leftHandles)
            newSpline.rightHandles.extend(spline.rightHandles)
    return newSpline

def allPolySplines(list splines):
    return all(isinstance(spline, PolySpline) for spline in splines)
