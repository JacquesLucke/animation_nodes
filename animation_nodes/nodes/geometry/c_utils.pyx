import cython
from libc.math cimport sqrt
from ... math cimport ( Vector3, dotVec3, scaleVec3, normalizeVec3,
    addVec3, subVec3, crossVec3, lengthVec3, lengthSquaredVec3,
    distanceVec3, toVector3, toPyVector3)
from ... data_structures cimport (
    Vector3DList, DoubleList, VirtualDoubleList,
    VirtualVector3DList, BooleanList, CharList)

cdef intersectLinePlane(Vector3 *lineStart, Vector3 *lineEnd,
                        Vector3 *planePoint, Vector3 *planeNormal,
                        Vector3 *outIntersection, double *outParameter, bint *outValid):
    cdef Vector3 direction, pointDirection, intersectionVector, intersection
    cdef double parameter, dot
    subVec3(&direction, lineEnd, lineStart)
    dot = dotVec3(planeNormal, &direction)
    if abs(dot) > 1e-6:
        subVec3(&pointDirection, lineStart, planePoint)
        factor = -dotVec3(planeNormal, &pointDirection) / dot
        scaleVec3(&intersectionVector, &direction, factor)
        addVec3(&intersection, lineStart, &intersectionVector)
        outIntersection[0] = intersection
        outParameter[0] = factor
        outValid[0] = True
    else:
        outIntersection[0] = Vector3(0,0,0)
        outParameter[0] = 0
        outValid[0] = False

def intersectLinePlaneList(Py_ssize_t amount,
                        VirtualVector3DList lineStartList,
                        VirtualVector3DList lineEndList,
                        VirtualVector3DList planePointList,
                        VirtualVector3DList planeNormalList):
    cdef Vector3DList intersectionList = Vector3DList(length = amount)
    cdef DoubleList parameterList = DoubleList(length = amount)
    cdef BooleanList validList = BooleanList(length = amount)
    cdef Vector3 intersection
    cdef double parameter
    cdef bint valid
    cdef Py_ssize_t i
    for i in range(amount):
        intersectLinePlane(lineStartList.get(i), lineEndList.get(i),
        planePointList.get(i), planeNormalList.get(i), &intersection, &parameter, &valid)
        intersectionList.data[i] = intersection
        parameterList.data[i] = parameter
        validList.data[i] = valid
    return intersectionList, parameterList, validList

def intersectLinePlaneSingle(lineStart,
                            lineEnd,
                            planePoint,
                            planeNormal):
    cdef Vector3 _lineStart = toVector3(lineStart)
    cdef Vector3 _lineEnd = toVector3(lineEnd)
    cdef Vector3 _planePoint = toVector3(planePoint)
    cdef Vector3 _planeNormal = toVector3(planeNormal)
    cdef Vector3 intersection
    cdef double parameter
    cdef bint valid
    intersectLinePlane(&_lineStart, &_lineEnd, &_planePoint, &_planeNormal,
    &intersection, &parameter, &valid)
    return toPyVector3(&intersection), parameter, valid

cdef intersectLineLine(Vector3 *firstLineStart, Vector3 *firstLineEnd,
                        Vector3 *secondLineStart, Vector3 *secondLineEnd,
                        Vector3 *outFirstNearestPoint, Vector3 *outSecondNearestPoint,
                        double *outFirstParameter, double *outSecondParameter, bint *outValid):
    cdef Vector3 direction1, direction2, normal, normal1, normal2, direction12, direction21
    cdef Vector3 scaledDirection1, scaledDirection2, nearestPointA, nearestPointB
    cdef double factor1, factor2
    subVec3(&direction1, firstLineEnd, firstLineStart)
    subVec3(&direction2, secondLineEnd, secondLineStart)
    crossVec3(&normal, &direction1, &direction2)
    if lengthVec3(&normal) > 1e-6:
        crossVec3(&normal1, &direction1, &normal)
        crossVec3(&normal2, &direction2, &normal)
        subVec3(&direction12, firstLineStart, secondLineStart)
        subVec3(&direction21, secondLineStart, firstLineStart)
        factor1 = dotVec3(&direction21, &normal2)/ dotVec3(&direction1, &normal2)
        factor2 = dotVec3(&direction12, &normal1)/ dotVec3(&direction2, &normal1)
        scaleVec3(&scaledDirection1, &direction1, factor1)
        scaleVec3(&scaledDirection2, &direction2, factor2)
        addVec3(&nearestPointA, firstLineStart, &scaledDirection1)
        addVec3(&nearestPointB, secondLineStart, &scaledDirection2)
        outFirstNearestPoint[0] = nearestPointA
        outSecondNearestPoint[0] = nearestPointB
        outFirstParameter[0] = factor1
        outSecondParameter[0] = factor2
        outValid[0] = True
    else:
        outFirstNearestPoint[0] = Vector3(0,0,0)
        outSecondNearestPoint[0] = Vector3(0,0,0)
        outFirstParameter[0] = 0
        outSecondParameter[0] = 0
        outValid[0] = False

def intersectLineLineList(Py_ssize_t amount,
                        VirtualVector3DList firstLineStartList,
                        VirtualVector3DList firstLineEndList,
                        VirtualVector3DList secondLineStartList,
                        VirtualVector3DList secondLineEndList):
    cdef Vector3DList firstNearestPointList = Vector3DList(length = amount)
    cdef Vector3DList secondNearestPointList = Vector3DList(length = amount)
    cdef DoubleList firstParameterList = DoubleList(length = amount)
    cdef DoubleList secondParameterList = DoubleList(length = amount)
    cdef BooleanList validList = BooleanList(length = amount)
    cdef Vector3 firstNearestPoint, secondNearestPoint
    cdef double firstParameter, secondParameter
    cdef bint valid
    cdef Py_ssize_t i
    for i in range(amount):
        intersectLineLine(firstLineStartList.get(i), firstLineEndList.get(i),
                        secondLineStartList.get(i), secondLineEndList.get(i),
                        &firstNearestPoint, &secondNearestPoint,
                        &firstParameter, &secondParameter, &valid)
        firstNearestPointList.data[i] = firstNearestPoint
        secondNearestPointList.data[i] = secondNearestPoint
        firstParameterList.data[i] = firstParameter
        secondParameterList.data[i] = secondParameter
        validList.data[i] = valid
    return firstNearestPointList, secondNearestPointList, firstParameterList, secondParameterList, validList

def intersectLineLineSingle(firstLineStart,
                            firstLineEnd,
                            secondLineStart,
                            secondLineEnd):
    cdef Vector3 _firstLineStart = toVector3(firstLineStart)
    cdef Vector3 _firstLineEnd = toVector3(firstLineEnd)
    cdef Vector3 _secondLineStart = toVector3(secondLineStart)
    cdef Vector3 _secondLineEnd = toVector3(secondLineEnd)
    cdef Vector3 firstNearestPoint, secondNearestPoint
    cdef double firstParameter, secondParameter
    cdef bint valid
    intersectLineLine(&_firstLineStart, &_firstLineEnd, &_secondLineStart, &_secondLineEnd,
    &firstNearestPoint, &secondNearestPoint, &firstParameter, &secondParameter, &valid)
    return toPyVector3(&firstNearestPoint), toPyVector3(&secondNearestPoint), firstParameter, secondParameter, valid

def IntersectLineSphere(Py_ssize_t amount,
                        VirtualVector3DList lineStart,
                        VirtualVector3DList lineEnd,
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
        subVec3(&direction, lineEnd.get(i), lineStart.get(i))
        subVec3(&startingPoint, lineStart.get(i), sphereCenter.get(i))
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
                addVec3(&_intersection1, lineStart.get(i), &_intersection1)
                addVec3(&_intersection2, lineStart.get(i), &_intersection2)
                intersection1.data[i] = _intersection1
                intersection2.data[i] = _intersection2
                intersection1Parameter.data[i] = factor1
                intersection2Parameter.data[i] = factor2
                numberOfIntersections.data[i] = 2
            else:
                factor = (-b + sqrt(discriminant))/(2 * a)
                scaleVec3(&_intersection1, &direction, factor)
                addVec3(&_intersection1, lineStart.get(i), &_intersection1)
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
                        VirtualVector3DList plane1Point,
                        VirtualVector3DList plane1Normal,
                        VirtualVector3DList plane2Point,
                        VirtualVector3DList plane2Normal):
    cdef Vector3DList lineDirection = Vector3DList(length = amount)
    cdef Vector3DList linePoint = Vector3DList(length = amount)
    cdef BooleanList valid = BooleanList(length = amount)
    cdef Vector3 direction, unitNormal1, unitNormal2, factor1, factor2, point
    cdef Py_ssize_t i
    for i in range(amount):
        normalizeVec3(&unitNormal1, plane1Normal.get(i))
        normalizeVec3(&unitNormal2, plane2Normal.get(i))
        crossVec3(&direction, plane1Normal.get(i), plane2Normal.get(i))
        if lengthVec3(&direction) > 1e-6:
            h1 = dotVec3(plane1Normal.get(i), plane1Point.get(i))
            h2 = dotVec3(plane2Normal.get(i), plane2Point.get(i))
            dot = dotVec3(plane1Normal.get(i), plane2Normal.get(i))
            invDotSquared = (1 - dot ** 2)
            c1 = (h1 - h2 * dot)/invDotSquared
            c2 = (h2 - h1 * dot)/invDotSquared
            scaleVec3(&factor1, plane1Normal.get(i), c1)
            scaleVec3(&factor2, plane2Normal.get(i), c2)
            addVec3(&point, &factor1, &factor2)
            lineDirection.data[i] = direction
            linePoint.data[i] = point
            valid.data[i] = True
        else:
            lineDirection.data[i] = Vector3(0,0,0)
            linePoint.data[i] = Vector3(0,0,0)
            valid.data[i] = False
    return lineDirection, linePoint, valid

def IntersectSpherePlane(Py_ssize_t amount,
                        VirtualVector3DList sphereCenter,
                        VirtualDoubleList sphereRadius,
                        VirtualVector3DList planePoint,
                        VirtualVector3DList planeNormal):
    cdef Vector3DList circleCenter = Vector3DList(length = amount)
    cdef DoubleList circleRadius = DoubleList(length = amount)
    cdef BooleanList valid = BooleanList(length = amount)
    cdef Vector3 direction, unitNormal, scaledNormal, center
    cdef double radius, distance
    cdef Py_ssize_t i
    for i in range(amount):
        normalizeVec3(&unitNormal, planeNormal.get(i))
        subVec3(&direction, sphereCenter.get(i), planePoint.get(i))
        distance = dotVec3(&direction, &unitNormal)
        if abs(distance) < sphereRadius.get(i):
            radius = sqrt(sphereRadius.get(i) ** 2 - distance ** 2)
            scaleVec3(&scaledNormal, &unitNormal, -distance)
            addVec3(&center, sphereCenter.get(i), &scaledNormal)
            circleCenter.data[i] = center
            circleRadius.data[i] = radius
            valid.data[i] = True
        else:
            circleCenter.data[i] = Vector3(0,0,0)
            circleRadius.data[i] = 0
            valid.data[i] = False
    return circleCenter, circleRadius, valid

def IntersectSphereSphere(Py_ssize_t amount,
                        VirtualVector3DList sphere1Center,
                        VirtualDoubleList sphere1Radius,
                        VirtualVector3DList sphere2Center,
                        VirtualDoubleList sphere2Radius):
    cdef Vector3DList circleCenter = Vector3DList(length = amount)
    cdef Vector3DList circleNormal = Vector3DList(length = amount)
    cdef DoubleList circleRadius = DoubleList(length = amount)
    cdef BooleanList valid = BooleanList(length = amount)
    cdef Vector3 direction, scaledDirection, center
    cdef double distance, r1, r2, h, r
    cdef Py_ssize_t i
    for i in range(amount):
        subVec3(&direction, sphere2Center.get(i), sphere1Center.get(i))
        distance = lengthVec3(&direction)
        r1 = sphere1Radius.get(i)
        r2 = sphere2Radius.get(i)
        if (distance <= (r1 + r2)) and ((distance + min(r1, r2)) >= max(r1, r2)) and (distance != 0):
            h = 0.5 + (r1 * r1 - r2 * r2)/(2 * distance * distance)
            scaleVec3(&scaledDirection, &direction, h)
            addVec3(&center, sphere1Center.get(i), &scaledDirection)
            r = sqrt(r1 * r1 - h * h * distance * distance)
            circleCenter.data[i] = center
            circleNormal.data[i] = direction
            circleRadius.data[i] = r
            valid.data[i] = True
        else:
            circleCenter.data[i] = Vector3(0,0,0)
            circleNormal.data[i] = Vector3(0,0,0)
            circleRadius.data[i] = 0
            valid.data[i] = False
    return circleCenter, circleNormal, circleRadius, valid

@cython.cdivision(True)
def ProjectPointOnLine(Py_ssize_t amount,
                    VirtualVector3DList lineStart,
                    VirtualVector3DList lineEnd,
                    VirtualVector3DList point):
    cdef Vector3DList Projection = Vector3DList(length = amount)
    cdef DoubleList Parameter = DoubleList(length = amount)
    cdef DoubleList Distance = DoubleList(length = amount)
    cdef Vector3 direction1, direction2, unitDirection, projVector, proj
    cdef double factor, length, param, distance
    cdef Py_ssize_t i
    for i in range(amount):
        subVec3(&direction1, lineEnd.get(i), lineStart.get(i))
        subVec3(&direction2, point.get(i), lineStart.get(i))
        normalizeVec3(&unitDirection, &direction1)
        factor = dotVec3(&direction2, &unitDirection)
        scaleVec3(&projVector, &unitDirection, factor)
        addVec3(&proj, lineStart.get(i), &projVector)
        length = lengthVec3(&direction1)
        param = factor / length if length != 0 else 0
        distance = distanceVec3(&projVector, point.get(i))
        Projection.data[i] = proj
        Parameter.data[i] = param
        Distance.data[i] = distance
    return Projection, Parameter, Distance

def ProjectPointOnPlane(Py_ssize_t amount,
                        VirtualVector3DList planePoint,
                        VirtualVector3DList planeNormal,
                        VirtualVector3DList point):
    cdef Vector3DList Projection = Vector3DList(length = amount)
    cdef DoubleList Distance = DoubleList(length = amount)
    cdef Vector3 direction, unitNormal, projVector, proj
    cdef double distance
    cdef Py_ssize_t i
    for i in range(amount):
        subVec3(&direction, point.get(i), planePoint.get(i))
        normalizeVec3(&unitNormal, planeNormal.get(i))
        distance = dotVec3(&direction, &unitNormal)
        scaleVec3(&projVector, &unitNormal, -distance)
        addVec3(&proj, point.get(i), &projVector)
        Projection.data[i] = proj
        Distance.data[i] = distance
    return Projection, Distance
