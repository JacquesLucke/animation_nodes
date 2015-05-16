from mathutils import Vector, Matrix

identityMatrix = Matrix.Identity(4)

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
        
    def transform(self, matrix = identityMatrix):
        for spline in self.splines:
            spline.transform(matrix)
        
        
class BezierSpline:
    def __init__(self):
        self.points = []
        self.segments = []
        self.isCyclic = False
        
    @staticmethod
    def fromBlenderSpline(blenderSpline):
        spline = BezierSpline()
        spline.isCyclic = blenderSpline.use_cyclic_u
        for blenderPoint in blenderSpline.bezier_points:
            point = BezierPoint.fromBlenderPoint(blenderPoint)
            spline.points.append(point)
        return spline
            
    def copy(self):
        spline = BezierSpline()
        spline.points = [point.copy() for point in self.points]
        return spline
        
    def transform(self, matrix = identityMatrix):
        for point in self.points:
            point.transform(matrix)
        
    def updateSegments(self):
        self.segments = []
        for left, right in zip(self.points[:-1], self.points[1:]):
            self.segments.append(BezierSegment(left, right))
        if self.isCyclic:
            self.segments.append(BezierSegment(self.points[-1], self.points[0]))
            
    def getSamples(self, amount):
        samples = []
        for i in range(amount - 1):
            samples.append(self.evaluate(i / (amount - 1)))
        samples.append(self.evaluate(1))
        return samples
        
    def evaluate(self, parameter):
        par = min(max(parameter, 0), 0.9999) * len(self.segments)
        return self.segments[int(par)].evaluate(par - int(par))
        
    def evaluateTangent(self, parameter):
        par = min(max(parameter, 0), 0.9999) * len(self.segments)
        return self.segments[int(par)].evaluateTangent(par - int(par))
        
    def calculateLength(self, samplesPerSegment = 5):
        length = 0
        for segment in self.segments:
            length += segment.calculateLength(samplesPerSegment)
        return length    
        
    @property
    def hasSegments(self):
        return len(self.segments) > 0
                
        
class BezierSegment:
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
        self.coeffs = [
            left.location,
            left.location * (-3.0) + left.rightHandle * (+3.0),
            left.location * (+3.0) + left.rightHandle * (-6.0) + right.leftHandle * (+3.0),
            left.location * (-1.0) + left.rightHandle * (+3.0) + right.leftHandle * (-3.0) + right.location]
            
    def evaluate(self, parameter):
        c = self.coeffs
        return c[0] + c[1] * parameter + c[2] * parameter ** 2 + c[3] * parameter ** 3
        
    def evaluateTangent(self, parameter):
        c = self.coeffs
        return c[1] + c[2] * 2 * parameter + c[3] * 3 * parameter ** 2
        
    def calculateLength(self, samples = 5):
        length = 0
        last = self.evaluate(0)
        for i in range(samples - 1):
            parameter = (i + 1) / (samples - 1)
            current = self.evaluate(parameter)
            length += (current - last).length
            last = current
        return length
        
        
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

    def transform(self, matrix = identityMatrix):
        self.location = matrix * self.location
        self.leftHandle = matrix * self.leftHandle
        self.rightHandle = matrix * self.rightHandle