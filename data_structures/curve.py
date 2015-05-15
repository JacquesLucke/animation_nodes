from mathutils import Vector


class BezierCurve:
    def __init__(self):
        self.splines = []
        
    @staticmethod
    def fromBlenderCurveData(blenderCurve):
        curve = BezierCurve()
        for blenderSpline in blenderCurve.splines:
            if blenderSpline.type == "BEZIER":
                spline = BezierSpline.fromBlenderSpline(blenderSpline)
                curve.splines.append(spline)
        return curve
            
    def copy(self):
        curve = BezierCurve()
        curve.splines = [spline.copy() for spline in self.splines]
        return curve
        
        
class BezierSpline:
    def __init__(self):
        self.points = []
        
    @staticmethod
    def fromBlenderSpline(blenderSpline):
        spline = BezierSpline()
        for blenderPoint in blenderSpline.bezier_points:
            point = BezierPoint.fromBlenderPoint(blenderPoint)
            spline.points.append(point)
        return spline
            
    def copy(self):
        spline = BezierSpline()
        spline.points = [point.copy() for point in self.points]
        return spline
        
        
class BezierPoint:
    def __init__(self):
        self.location = Vector((0, 0, 0))
        self.leftHandle = Vector((0, 0, 0))
        self.rightHandle = Vector((0, 0, 0))
        
    @staticmethod
    def fromBlenderPoint(blenderPoint):
        point = BezierPoint()
        point.location = blenderPoint.co
        point.leftHandle = blenderPoint.handle_left
        point.rightHandle = blenderPoint.handle_right
        return point
        
    def copy(self):
        point = BezierPoint()
        point.location = self.location.copy()
        point.leftHandle = self.leftHandle.copy()
        point.rightHandle = self.rightHandle.copy()
        return point