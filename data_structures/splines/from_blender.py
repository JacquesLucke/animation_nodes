from . bezier_spline import BezierSpline, BezierPoint

def createSplinesFromBlenderObject(object):
    if object is None: return []
    if object.type != "CURVE": return []
    
    splines = []
    
    for bSpline in object.data.splines:
        if bSpline.type == "BEZIER":
            splines.append(createBezierSpline(bSpline))
            
    return splines
            
def createBezierSpline(bSpline):
    bezierSpline = BezierSpline()
    bezierSpline.isCyclic = bSpline.use_cyclic_u
    for bPoint in bSpline.bezier_points:
        point = BezierPoint(bPoint.co, bPoint.handle_left, bPoint.handle_right)
        bezierSpline.points.append(point)
    return bezierSpline