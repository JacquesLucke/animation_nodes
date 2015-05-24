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
    
    for i, point in enumerate(spline.points):
        bPoint = bSpline.bezier_points[i]
        bPoint.co = point.location
        bPoint.handle_left = point.leftHandle
        bPoint.handle_right = point.rightHandle
        
        
def appendPolySpline(bSplines, spline):
    bSpline = bSplines.new("POLY")
    bSpline.use_cyclic_u = spline.isCyclic
    
    # one point is already there
    bSpline.points.add(len(spline.points) - 1)
    
    for i, point in enumerate(spline.points):
        bSpline.points[i].co = Vector((list(point) + [0]))