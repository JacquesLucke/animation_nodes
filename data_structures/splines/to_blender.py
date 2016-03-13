from itertools import chain
from mathutils import Vector

def setSplinesOnBlenderObject(object, splines):
    if object is None: return
    if object.type != "CURVE": return

    bSplines = object.data.splines
    bSplines.clear()
    for spline in splines:
        if spline.type == "BEZIER":
            appendBezierSpline(bSplines, spline)
        if spline.type == "POLY":
            appendPolySpline(bSplines, spline)


def appendBezierSpline(bSplines, spline):
    bSpline = bSplines.new("BEZIER")
    bSpline.use_cyclic_u = spline.isCyclic

    # one point is already there
    bSpline.bezier_points.add(len(spline.points) - 1)

    locations = tuple(chain.from_iterable(point.location for point in spline.points))
    leftHandles = tuple(chain.from_iterable(point.leftHandle for point in spline.points))
    rightHandles = tuple(chain.from_iterable(point.rightHandle for point in spline.points))

    bSpline.bezier_points.foreach_set("co", locations)
    bSpline.bezier_points.foreach_set("handle_left", leftHandles)
    bSpline.bezier_points.foreach_set("handle_right", rightHandles)


def appendPolySpline(bSplines, spline):
    bSpline = bSplines.new("POLY")
    bSpline.use_cyclic_u = spline.isCyclic

    # one point is already there
    bSpline.points.add(len(spline.points) - 1)

    # points of poly splines have 4 values
    nullList = [0]
    locations = tuple(chain.from_iterable(list(point) + nullList for point in spline.points))
    bSpline.points.foreach_set("co", locations)
