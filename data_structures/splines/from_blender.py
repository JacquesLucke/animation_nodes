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
    raise NotImplementedError()
