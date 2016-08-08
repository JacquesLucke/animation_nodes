from . poly_spline import PolySpline
from .. import FloatList, Vector3DList

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
    raise NotImplementedError()

def createPolySpline(bSpline):
    pointArray = FloatList(length = 4 * len(bSpline.points))
    del pointArray[3::4]
    splinePoints = Vector3DList.fromBaseList(pointArray)

    spline = PolySpline(splinePoints)
    spline.cyclic = bSpline.use_cyclic_u
    return spline
