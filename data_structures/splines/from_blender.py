from mathutils import Vector
from . bezier_spline import BezierSpline, BezierPoint
from . poly_spline import PolySpline

def createSplinesFromBlenderObject(object):
    if object is None: return []
    if object.type != "CURVE": return []
    
    splines = []
    
    for bSpline in object.data.splines:
        if bSpline.type == "BEZIER":
            splines.append(createBezierSpline(bSpline))
        if bSpline.type == "POLY":
            splines.append(createPolySpline(bSpline))
    return splines
            
def createBezierSpline(bSpline):
    bezierSpline = BezierSpline()
    bezierSpline.isCyclic = bSpline.use_cyclic_u
    for bPoint in bSpline.bezier_points:
        point = BezierPoint(bPoint.co, bPoint.handle_left, bPoint.handle_right)
        bezierSpline.points.append(point)
    return bezierSpline
    
def createPolySpline(bSpline):
    polySpline = PolySpline()
    polySpline.isCyclic = bSpline.use_cyclic_u
    for bPoint in bSpline.points:
        polySpline.points.append(Vector((bPoint.co[:3])))
    return polySpline    