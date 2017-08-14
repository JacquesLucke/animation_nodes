from libc.math cimport sqrt
from ... math cimport ( Vector3, dotVec3, scaleVec3, normalizeVec3,
    addVec3, subVec3, crossVec3, lengthVec3, lengthSquaredVec3)
from ... data_structures cimport (
    Vector3DList, DoubleList, VirtualDoubleList,
    VirtualVector3DList, BooleanList, CharList)

def IntersectLinePlane(Py_ssize_t amount,
                      VirtualVector3DList lineStart,
                      VirtualVector3DList lineEnd,
                      VirtualVector3DList planePoint,
                      VirtualVector3DList planeNormal):
    cdef Vector3DList intersection = Vector3DList(length = amount)
    cdef DoubleList parameter = DoubleList(length = amount)
    cdef BooleanList valid = BooleanList(length = amount)
    cdef Vector3 direction, pointDirection, _intersection, intersectionVector
    cdef double factor
    cdef Py_ssize_t i
    for i in range(amount):
        subVec3(&direction, lineEnd.get(i), lineStart.get(i))
        dot = dotVec3(planeNormal.get(i), &direction)
        if abs(dot) > 1e-6:
            subVec3(&pointDirection, lineStart.get(i), planePoint.get(i))
            factor = -dotVec3(planeNormal.get(i), &pointDirection) / dot
            scaleVec3(&intersectionVector, &direction, factor)
            addVec3(&_intersection, lineStart.get(i), &intersectionVector)
            intersection.data[i] = _intersection
            parameter.data[i] = factor
            valid.data[i] = True
        else:
            intersection.data[i] = Vector3(0,0,0)
            parameter.data[i] = 0
            valid.data[i] = False
    return intersection, parameter, valid

def IntersectLineLine(Py_ssize_t amount,
                    VirtualVector3DList firstLineStart,
                    VirtualVector3DList firstLineEnd,
                    VirtualVector3DList secondLineStart,
                    VirtualVector3DList secondLineEnd):
    cdef Vector3DList nearestPoint1 = Vector3DList(length = amount)
    cdef Vector3DList nearestPoint2 = Vector3DList(length = amount)
    cdef DoubleList firstParameter = DoubleList(length = amount)
    cdef DoubleList secondParameter = DoubleList(length = amount)
    cdef BooleanList valid = BooleanList(length = amount)
    cdef Vector3 direction1, direction2, normal, normal1, normal2, direction12, direction21
    cdef Vector3 scaledDirection1, scaledDirection2, nearestPointA, nearestPointB
    cdef double factor1, factor2
    cdef Py_ssize_t i
    for i in range(amount):
        subVec3(&direction1, firstLineEnd.get(i), firstLineStart.get(i))
        subVec3(&direction2, secondLineEnd.get(i), secondLineStart.get(i))
        crossVec3(&normal, &direction1, &direction2)
        if lengthVec3(&normal) > 1e-6:
            valid.data[i] = True
            crossVec3(&normal1, &direction1, &normal)
            crossVec3(&normal2, &direction2, &normal)
            subVec3(&direction12, firstLineStart.get(i), secondLineStart.get(i))
            subVec3(&direction21, secondLineStart.get(i), firstLineStart.get(i))
            factor1 = dotVec3(&direction21, &normal2)/ dotVec3(&direction1, &normal2)
            factor2 = dotVec3(&direction12, &normal1)/ dotVec3(&direction2, &normal1)
            firstParameter.data[i] = factor1
            secondParameter.data[i] = factor2
            scaleVec3(&scaledDirection1, &direction1, factor1)
            scaleVec3(&scaledDirection2, &direction2, factor2)
            addVec3(&nearestPointA, firstLineStart.get(i), &scaledDirection1)
            addVec3(&nearestPointB, secondLineStart.get(i), &scaledDirection2)
            nearestPoint1.data[i] = nearestPointA
            nearestPoint2.data[i] = nearestPointB
        else:
            valid.data[i] = False
            firstParameter.data[i] = 0
            secondParameter.data[i] = 0
            nearestPoint1.data[i] = Vector3(0,0,0)
            nearestPoint2.data[i] = Vector3(0,0,0)
    return nearestPoint1, nearestPoint2, firstParameter, secondParameter, valid

def IntersectLineSphere(Py_ssize_t amount,
                        VirtualVector3DList LineStart,
                        VirtualVector3DList LineEnd,
                        VirtualVector3DList sphereCenter,
                        VirtualDoubleList sphereRadius):
    cdef Vector3DList intersection1 = Vector3DList(length = amount)
    cdef Vector3DList intersection2 = Vector3DList(length = amount)
    cdef DoubleList intersection1Parameter = DoubleList(length = amount)
    cdef DoubleList intersection2Parameter = DoubleList(length = amount)
    cdef CharList numberOfIntersections = CharList(length = amount)
    cdef Vector3 direction, startingPoint, _intersection1, _intersection2
    cdef double factor1, factor2, a, b, c
    cdef Py_ssize_t i
    for i in range(amount):
        subVec3(&direction, LineEnd.get(i), LineStart.get(i))
        subVec3(&startingPoint, LineStart.get(i), sphereCenter.get(i))
        a = lengthSquaredVec3(&direction)
        b = dotVec3(&direction, &startingPoint) * 2
        c = lengthSquaredVec3(&startingPoint) - sphereRadius.get(i) ** 2
        discriminant = b ** 2 - 4 * a * c
        if discriminant > 0:
            if discriminant > 1e-6:
                sqrtDiscriminant = sqrt(discriminant)
                factor1 = (-b + sqrtDiscriminant)/(2 * a)
                factor2 = (-b - sqrtDiscriminant)/(2 * a)
                scaleVec3(&_intersection1, &direction, factor1)
                scaleVec3(&_intersection2, &direction, factor2)
                addVec3(&_intersection1, LineStart.get(i), &_intersection1)
                addVec3(&_intersection2, LineStart.get(i), &_intersection2)
                intersection1.data[i] = _intersection1
                intersection2.data[i] = _intersection2
                intersection1Parameter.data[i] = factor1
                intersection2Parameter.data[i] = factor2
                numberOfIntersections.data[i] = 2
            else:
                factor = (-b + sqrt(discriminant))/(2 * a)
                scaleVec3(&_intersection1, &direction, factor)
                addVec3(&_intersection1, LineStart.get(i), &_intersection1)
                intersection1.data[i] = _intersection1
                intersection2.data[i] = _intersection1
                intersection1Parameter.data[i] = factor
                intersection2Parameter.data[i] = factor
                numberOfIntersections.data[i] = 1
        else:
            intersection1.data[i] = Vector3(0,0,0)
            intersection2.data[i] = Vector3(0,0,0)
            intersection1Parameter.data[i] = 0
            intersection2Parameter.data[i] = 0
            numberOfIntersections.data[i] = 0

    return intersection1, intersection2, intersection1Parameter, intersection2Parameter, numberOfIntersections

def IntersectPlanePlane(Py_ssize_t amount,
                        VirtualVector3DList Plane1Point,
                        VirtualVector3DList Plane1Normal,
                        VirtualVector3DList Plane2Point,
                        VirtualVector3DList Plane2Normal):
    cdef Vector3DList lineDirection = Vector3DList(length = amount)
    cdef Vector3DList linePoint = Vector3DList(length = amount)
    cdef BooleanList valid = BooleanList(length = amount)
    cdef Vector3 direction, unitNormal1, unitNormal2, factor1, factor2, point
    cdef Py_ssize_t i
    for i in range(amount):
        normalizeVec3(&unitNormal1, Plane1Normal.get(i))
        normalizeVec3(&unitNormal2, Plane2Normal.get(i))
        crossVec3(&direction, Plane1Normal.get(i), Plane2Normal.get(i))
        if lengthVec3(&direction) > 1e-6:
            h1 = dotVec3(Plane1Normal.get(i), Plane1Point.get(i))
            h2 = dotVec3(Plane2Normal.get(i), Plane2Point.get(i))
            dot = dotVec3(Plane1Normal.get(i), Plane2Normal.get(i))
            invDotSquared = (1 - dot ** 2)
            c1 = (h1 - h2 * dot)/invDotSquared
            c2 = (h2 - h1 * dot)/invDotSquared
            scaleVec3(&factor1, Plane1Normal.get(i), c1)
            scaleVec3(&factor2, Plane2Normal.get(i), c2)
            addVec3(&point, &factor1, &factor2)
            lineDirection.data[i] = direction
            linePoint.data[i] = point
            valid.data[i] = True
        else:
            lineDirection.data[i] = Vector3(0,0,0)
            linePoint.data[i] = Vector3(0,0,0)
            valid.data[i] = False
    return lineDirection, linePoint, valid
