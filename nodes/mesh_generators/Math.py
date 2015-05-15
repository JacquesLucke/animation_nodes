import mathutils
from mathutils import *
import math


limitDistance = 0.00001




def IsSamePoint(v31, v32):
    global limitDistance
    
    if (v31 - v32).magnitude < limitDistance: return True
    
    return False
    
    
def IsZero(flt):
    global limitDistance
    
    if math.fabs(flt) < limitDistance: return True
    
    return False
    
    
    
    

# makes 0 <= angle < 2pi    
def ToPositiveAngle(fltAng):
    pi2 = math.pi * 2.0
    rvAng = fltAng
    
    while rvAng < 0.0: rvAng += pi2
    while rvAng >= pi2: rvAng -= pi2
    
    return rvAng
    
    
def DistanceAngles(fltAng1, fltAng2):
    pi2 = math.pi * 2.0
    
    dist = math.fabs(fltAng1 - fltAng2)
    
    ndist = math.fabs(fltAng1 - fltAng2 + pi2)
    if ndist < dist: dist = ndist
    ndist = math.fabs(fltAng1 - fltAng2 - pi2)
    if ndist < dist: dist = ndist
    
    return dist


# distance from fltAng1 to fltAng2 when moving CCW
# angles must be in 0 .. 2pi
def DistanceAnglesCCW(fltAng1, fltAng2):
    pi2 = math.pi * 2.0
    
    diff21 = fltAng2 - fltAng1
    if diff21 > 0.0: return diff21
    
    return pi2 + diff21


# distance from fltAng1 to fltAng2 when moving CW
# angles must be in 0 .. 2pi
def DistanceAnglesCW(fltAng1, fltAng2):
    pi2 = math.pi * 2.0
    
    diff21 = fltAng1 - fltAng2
    if diff21 > 0.0: return diff21
    
    return pi2 + diff21
    

def GetDirXY(fltAng):
    return Vector((math.cos(fltAng), math.sin(fltAng), 0.0))
    
    
def ExtendToMaxAngle(listAngles, fltMaxAngle):
    rvList = list(listAngles)
    
    cont = True
    while cont:
        cont = False
        nrAngles = len(rvList)
        for iAngle in range(nrAngles):
            currAngle = rvList[iAngle]
            nextIndex = iAngle + 1
            if nextIndex >= nrAngles: nextIndex = 0
            nextAngle = rvList[nextIndex]
            distAngles = DistanceAnglesCCW(currAngle, nextAngle)
            if distAngles > fltMaxAngle:
                rndf = mathutils.noise.random()

                newAngle = ToPositiveAngle(currAngle + distAngles * rndf)
                rvList.insert(nextIndex, newAngle)
                cont = True
                break
                
    return rvList
                
        
def ToAnglesInBetween(listAngles):
    rvList = list()
    nrAngles = len(listAngles)
    for iAngle in range(nrAngles - 1):
        currAng = listAngles[iAngle]
        nextAng = listAngles[iAngle + 1]
        rvList.append(currAng + 0.5 * (nextAng - currAng))
        
    firstAng = listAngles[0]
    lastAng2 = ToPositiveAngle(nextAng + 0.5 * DistanceAnglesCCW(nextAng, firstAng))
                
    return sorted(rvList)
    
    
    
    
    
# solves ax + b = 0
def LinearRoot(a, b):
    if IsZero(a): return None
    
    return - b / a
    

# solves ax^2 + bx + c = 0
def QuadraticRoots(a, b, c):
    if IsZero(a):
        lr = LinearRoot(b, c)
        return (lr, lr)
    
    discriminant = b * b - (4.0 * a * c)
    if discriminant < 0.0: return None
    
    rm = (-b - math.sqrt(discriminant)) / (2.0 * a)
    rp = (-b + math.sqrt(discriminant)) / (2.0 * a)
    
    return (rm, rp)
    
    
# solves A*sin(x) + B*cos(x) + C = 0
# http://in.answers.yahoo.com/question/index?qid=20100123004704AAc6Gg7 -- answer by Moise Gunen
def SolveAsinBcosC0(A, B, C):
    sqrtA2B2 = math.sqrt(A * A + B * B)
    try:
        COversqrtA2B2 = C / sqrtA2B2
        if math.fabs(COversqrtA2B2) > 1: return None
    except:
        return None
        
    arctanBA = math.atan2(B, A)
    arcsin = math.asin(- COversqrtA2B2)
    
    x1 = (- arctanBA) + arcsin
    x2 = ((- arctanBA) - arcsin) + math.pi
    
    return (x1, x2)
    
    
# http://geomalgorithms.com/a07-_distance.html
def CalcClosestPointLines(v3P0, v3P1, v3Q0, v3Q1):
    u = v3P1 - v3P0
    v = v3Q1 - v3Q0
    
    w0 = v3P0 - v3Q0
    a = u.dot(u)
    b = u.dot(v)
    c = v.dot(v)
    d = u.dot(w0)
    e = v.dot(w0)
    
    rvv3 = (v3P0 + v3P1 + v3Q0 + v3Q1) * 0.25
    
    try: sc = (b * e - c * d) / (a * c - b * b)
    except: sc = None
    if sc is None: return rvv3
    
    try: tc = (a * e - b * d) / (a * c - b * b)
    except: tc = None
    if tc is None: return rvv3
    
    rvv3p = v3P0 + (u * sc)
    rvv3q = v3Q0 + (v * tc)
    rvv3 = (rvv3p + rvv3q) * 0.5
    
    return rvv3
    

    
    
    
    
class Line(object):
    def __init__(self, v3Pos, v3Dir):
        self.pos = v3Pos
        self.dir = v3Dir
        
        
    def CalcPoint(self, par):
        return self.pos + (self.dir * par)
        
        
    def CalcParClosestToPoint(self, v3Point):
        return (v3Point - self.pos).dot(self.dir)