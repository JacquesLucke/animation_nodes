from mathutils import Vector
from . bezier_spline import BezierSpline, BezierPoint
from . poly_spline import PolySpline

def createSplinesFromBlenderObject(object):
    if object is None: return []
    if object.type != "CURVE": return []

    splines = []

    for bSpline in object.data.splines:
        spline = createSplineFromBlenderSpline(bSpline)
        if spline is not None:
            splines.append(spline)
    return splines

def createSplineFromBlenderSpline(bSpline):
    if bSpline.type == "BEZIER":
        return createBezierSpline(bSpline)
    elif bSpline.type == "POLY":
        return createPolySpline(bSpline)
    return None

def createBezierSpline(bSpline):
    pointAmount = len(bSpline.bezier_points)
    positionsData = [None] * (pointAmount * 3)
    leftHandlesData = [None] * (pointAmount * 3)
    rightHandlesData = [None] * (pointAmount * 3)

    bSpline.bezier_points.foreach_get("co", positionsData)
    bSpline.bezier_points.foreach_get("handle_left", leftHandlesData)
    bSpline.bezier_points.foreach_get("handle_right", rightHandlesData)

    # create (x, y, z) tuples from flattened position data
    positionsIterator = map(Vector, zip(*([iter(positionsData)] * 3)))
    leftHandlesIterator = map(Vector, zip(*([iter(leftHandlesData)] * 3)))
    rightHandlesIterator = map(Vector, zip(*([iter(rightHandlesData)] * 3)))

    bezierSpline = BezierSpline()
    bezierSpline.points = list(map(BezierPoint, positionsIterator, leftHandlesIterator, rightHandlesIterator))
    bezierSpline.isCyclic = bSpline.use_cyclic_u

    return bezierSpline

def createPolySpline(bSpline):
    polySpline = PolySpline()
    polySpline.isCyclic = bSpline.use_cyclic_u
    for bPoint in bSpline.points:
        polySpline.points.append(Vector((bPoint.co[:3])))
    return polySpline
