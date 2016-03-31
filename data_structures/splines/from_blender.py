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
    pointAmount = len(bSpline.bezier_points)
    positionsData = [None] * (pointAmount * 3)
    leftHandlesData = [None] * (pointAmount * 3)
    rightHandlesData = [None] * (pointAmount * 3)

    bSpline.bezier_points.foreach_get("co", positionsData)
    bSpline.bezier_points.foreach_get("handle_left", leftHandlesData)
    bSpline.bezier_points.foreach_get("handle_right", rightHandlesData)

    # create Vector objects from flattened position data
    positionsDataIterator = positionsData.__iter__()
    leftHandlesDataIterator = leftHandlesData.__iter__()
    rightHandlesDataIterator = rightHandlesData.__iter__()

    positionsIterator = map(Vector, zip(positionsDataIterator, positionsDataIterator, positionsDataIterator))
    leftHandlesIterator = map(Vector, zip(leftHandlesDataIterator, leftHandlesDataIterator, leftHandlesDataIterator))
    rightHandlesIterator = map(Vector, zip(rightHandlesDataIterator, rightHandlesDataIterator, rightHandlesDataIterator))

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
