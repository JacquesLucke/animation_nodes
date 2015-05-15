from mathutils import Vector


class BezierCurve:
    def __init__(self):
        self.splines = []
        
    @staticmethod
    def fromBlenderCurveData(blenderCurve):
        curve = BezierCurve()
        for blenderSpline in blenderCurve.splines:
            spline = BezierSpline.fromBlenderSpline(blenderSpline)
            curve.splines.append(spline)
        
        
class BezierSpline:
    def __init__(self):
        self.points = []
        
    @staticmethod
    def fromBlenderSpline(blenderSpline):
        spline = BezierSpline()
        for blenderPoint in blenderSpline.bezier_points:
            point = BezierPoint.fromBlenderPoint(blenderPoint)
            spline.points.append(point)
        
        
class BezierPoint:
    def __init__(self, location = Vector((0, 0, 0)), 
                       leftHandle = Vector((0, 0, 0)), 
                       rightHandle = Vector((0, 0, 0))):
        self.location = location
        self.leftHandle = leftHandle
        self.rightHandle = rightHandle
        
    @staticmethod
    def fromBlenderPoint(blenderPoint):
        point = BezierPoint()
        point.location = blenderPoint.co
        point.leftHandle = blenderPoint.handle_left
        point.rightHandle = blenderPoint.handle_right