from . bezier_spline import BezierSpline
from . poly_spline import PolySpline

def connectSplines(splines):
    if len(splines) == 0: return BezierSpline()
    if len(splines) == 1: return splines[0].copy()
    
    if areAllPolySplines(splines): newSpline = PolySpline()
    else: newSpline = BezierSpline()
    
    for spline in splines:
        if spline.type == "BEZIER":
            for bezierPoint in spline.points:
                newSpline.points.append(bezierPoint)
        elif spline.type == "POLY":
            newSpline.appendPoints(spline.points)
        
    return newSpline
    
def areAllPolySplines(splines):
    return all([spline.type == "POLY" for spline in splines])  