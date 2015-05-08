import math
import numpy
from mathutils import *


defaultDeltaImaginary = 0.00001
def ComplexToRealFloat(complex, deltaImaginary = defaultDeltaImaginary):
    try:
        if type(complex) is numpy.float_: return float(complex)
        
        if type(complex) is numpy.complex_:
            if math.fabs(complex.imag) < deltaImaginary: return float(complex.real)
    except: return None
        

def IsSamePoint(v31, v32, limitDistance):
    if (v31 - v32).magnitude < limitDistance: return True

    return False


class Plane:
    @staticmethod
    def XY():
        p1 = Vector((0, 0, 0))
        p2 = Vector((1, 0, 0))
        p3 = Vector((0, 1, 0))

        return Plane(p1, p2, p3)


    # plane equation: (p - position).dot(normal) = 0
    def __init__(self, P1, P2, P3):
        self.normal = (P2 - P1).cross(P3 - P1)
        self.normal.normalize()

        self.position = P1


    def CalcIntersectionPointLineSegment(self, PL1, PL2):
        DL = PL2 - PL1

        try: rvPar = ((self.position - PL1).dot(self.normal)) / (DL.dot(self.normal))
        except: return None

        return rvPar


    def CalcNormalParameter(self, vector):
        return (vector - self.position).dot(self.normal)


    def CalcProjection(self, vector):
        normalParameter = self.CalcNormalParameter(vector)

        rvv3 = vector - (self.normal * normalParameter)

        return [normalParameter, rvv3]



# http://geomalgorithms.com/a07-_distance.html
def CalcClosestPointLineSegments(v3P0, v3P1, v3Q0, v3Q1):
    u = v3P1 - v3P0
    v = v3Q1 - v3Q0

    w0 = v3P0 - v3Q0
    a = u.dot(u)
    b = u.dot(v)
    c = v.dot(v)
    d = u.dot(w0)
    e = v.dot(w0)


    try: parP = (b * e - c * d) / (a * c - b * b)
    except: return None

    try: parQ = (a * e - b * d) / (a * c - b * b)
    except: return None


    return [parP, parQ]


def CalcIntersectionPointLineSegments(v3P0, v3P1, v3Q0, v3Q1, limitDistance):
    rvList = CalcClosestPointLineSegments(v3P0, v3P1, v3Q0, v3Q1)
    if rvList is None: return None


    parP = rvList[0]
    if parP < 0.0: return None
    if parP > 1.0: return None

    parQ = rvList[1]
    if parQ < 0.0: return None
    if parQ > 1.0: return None


    pointP = v3P0 + ((v3P1 - v3P0) * parP)
    pointQ = v3Q0 + ((v3Q1 - v3Q0) * parQ)
    if not IsSamePoint(pointP, pointQ, limitDistance): return None

    return [parP, parQ, pointP, pointQ]


def CalcIntersectionPointsLineSegmentsPOV(v3P0, v3P1, v3Q0, v3Q1, v3POV):
    planeQ = Plane(v3POV, v3Q0, v3Q1)
    parP = planeQ.CalcIntersectionPointLineSegment(v3P0, v3P1)
    if parP is None: return None
    if parP < 0.0: return None
    if parP > 1.0: return None

    planeP = Plane(v3POV, v3P0, v3P1)
    parQ = planeP.CalcIntersectionPointLineSegment(v3Q0, v3Q1)
    if parQ is None: return None
    if parQ < 0.0: return None
    if parQ > 1.0: return None

    return [parP, parQ]


def CalcIntersectionPointsLineSegmentsDIR(v3P0, v3P1, v3Q0, v3Q1, v3DIR):
    v3POV = v3Q0 + v3DIR
    planeQ = Plane(v3POV, v3Q0, v3Q1)
    parP = planeQ.CalcIntersectionPointLineSegment(v3P0, v3P1)
    if parP is None: return None
    if parP < 0.0: return None
    if parP > 1.0: return None

    v3POV = v3P0 + v3DIR
    planeP = Plane(v3POV, v3P0, v3P1)
    parQ = planeP.CalcIntersectionPointLineSegment(v3Q0, v3Q1)
    if parQ is None: return None
    if parQ < 0.0: return None
    if parQ > 1.0: return None

    return [parP, parQ]



def CalcRotationMatrix(v3From, v3To):
    cross = v3From.cross(v3To)

    try: angle = v3From.angle(v3To)
    except: return Matrix.Identity(4)

    return Matrix.Rotation(angle, 4, cross)        # normalize axis?


# lineDir is supposed to be normalized
def CalcProjectionPointToLine(point, linePos, lineDir):
    pos2point = point - linePos
    dotProduct = lineDir.dot(pos2point)
    rvPoint = linePos + (lineDir * dotProduct)
    
    return rvPoint

# if resolution == 4, the last point is at 270°, so you may need to 'make it cyclic' yourself
def GenerateCircle(center, radius, dirX, dirY, resolution):
    currAng = 0.0
    deltaAng = (math.pi * 2.0) / float(resolution)
    rvVectors = []

    for iAngle in range(resolution):
        cosAngle = math.cos(currAng)
        sinAngle = math.sin(currAng)

        currVector = center + (dirX * radius * cosAngle) + (dirY * radius * sinAngle)
        rvVectors.append(currVector)

        currAng = currAng + deltaAng

    return rvVectors