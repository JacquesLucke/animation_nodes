import cython
from libc.math cimport sqrt
from ... math cimport ( Vector3, dotVec3, scaleVec3, normalizeVec3,
    addVec3, subVec3, crossVec3, lengthVec3, lengthSquaredVec3,
    distanceVec3, toVector3, toPyVector3)
from ... data_structures cimport (
    Vector3DList, DoubleList, VirtualDoubleList,
    VirtualVector3DList, BooleanList, CharList)

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
    return (firstNearestPointList, secondNearestPointList,
    firstParameterList, secondParameterList, validList)

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
    return (toPyVector3(&firstNearestPoint), toPyVector3(&secondNearestPoint),
    firstParameter, secondParameter, valid)

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

cdef intersectLineSphere(Vector3 *lineStart, Vector3 *lineEnd,
                        Vector3 *sphereCenter, double sphereRadius,
                        Vector3 *outFirstIntersection, Vector3 *outSecondIntersection,
                        double *outFirstParameter, double *outSecondParameter,
                        char *outNumberOfIntersections):
    cdef Vector3 direction, startingPoint, firstIntersection, secondIntersection
    cdef double factor1, factor2, a, b, c, sqrtDiscriminant, discriminant
    subVec3(&direction, lineEnd, lineStart)
    subVec3(&startingPoint, lineStart, sphereCenter)
    a = lengthSquaredVec3(&direction)
    b = dotVec3(&direction, &startingPoint) * 2
    c = lengthSquaredVec3(&startingPoint) - sphereRadius * sphereRadius
    discriminant = b ** 2 - 4 * a * c
    if discriminant > 0:
        if discriminant > 1e-6:
            sqrtDiscriminant = sqrt(discriminant)
            factor1 = (-b + sqrtDiscriminant)/(2 * a)
            factor2 = (-b - sqrtDiscriminant)/(2 * a)
            scaleVec3(&firstIntersection, &direction, factor1)
            scaleVec3(&secondIntersection, &direction, factor2)
            addVec3(&firstIntersection, lineStart, &firstIntersection)
            addVec3(&secondIntersection, lineStart, &secondIntersection)
            outFirstIntersection[0] = firstIntersection
            outSecondIntersection[0] = secondIntersection
            outFirstParameter[0] = factor1
            outSecondParameter[0] = factor2
            outNumberOfIntersections[0] = 2
        else:
            factor = (-b + sqrt(discriminant))/(2 * a)
            scaleVec3(&firstIntersection, &direction, factor)
            addVec3(&firstIntersection, lineStart, &firstIntersection)
            outFirstIntersection[0] = firstIntersection
            outSecondIntersection[0] = firstIntersection
            outFirstParameter[0] = factor
            outSecondParameter[0] = factor
            outNumberOfIntersections[0] = 1
    else:
        outFirstIntersection[0] = Vector3(0,0,0)
        outSecondIntersection[0] = Vector3(0,0,0)
        outFirstParameter[0] = 0
        outSecondParameter[0] = 0
        outNumberOfIntersections[0] = 0

def intersectLineSphereList(Py_ssize_t amount,
                            VirtualVector3DList lineStartList,
                            VirtualVector3DList lineEndList,
                            VirtualVector3DList sphereCenterList,
                            VirtualDoubleList sphereRadiusList):
    cdef Vector3DList firstIntersectionList = Vector3DList(length = amount)
    cdef Vector3DList secondIntersectionList = Vector3DList(length = amount)
    cdef DoubleList firstParameterList = DoubleList(length = amount)
    cdef DoubleList secondParameterList = DoubleList(length = amount)
    cdef CharList numberOfIntersectionsList = CharList(length = amount)
    cdef Vector3 firstIntersection, secondIntersection
    cdef double firstParameter, secondParameter
    cdef char numberOfIntersections
    cdef Py_ssize_t i
    for i in range(amount):
        intersectLineSphere(lineStartList.get(i), lineEndList.get(i),
        sphereCenterList.get(i), sphereRadiusList.get(i),
        &firstIntersection, &secondIntersection,
        &firstParameter, &secondParameter, &numberOfIntersections)
        firstIntersectionList.data[i] = firstIntersection
        secondIntersectionList.data[i] = secondIntersection
        firstParameterList.data[i] = firstParameter
        secondParameterList.data[i] = secondParameter
        numberOfIntersectionsList.data[i] = numberOfIntersections
    return (firstIntersectionList, secondIntersectionList,
            firstParameterList, secondParameterList,
            numberOfIntersectionsList)

def intersectLineSphereSingle(lineStart,
                            lineEnd,
                            sphereCenter,
                            sphereRadius):
    cdef Vector3 _lineStart = toVector3(lineStart)
    cdef Vector3 _lineEnd = toVector3(lineEnd)
    cdef Vector3 _sphereCenter = toVector3(sphereCenter)
    cdef Vector3 firstIntersection, secondIntersection
    cdef double firstParameter, secondParameter
    cdef char numberOfIntersections
    intersectLineSphere(&_lineStart, &_lineEnd, &_sphereCenter, sphereRadius,
    &firstIntersection, &secondIntersection, &firstParameter, &secondParameter, &numberOfIntersections)
    return (toPyVector3(&firstIntersection), toPyVector3(&secondIntersection),
            firstParameter, secondParameter,
            numberOfIntersections)

cdef intersectPlanePlane(Vector3 *firstPlanePoint, Vector3 *firstPlaneNormal,
                        Vector3 *secondPlanePoint, Vector3 *secondPlaneNormal,
                        Vector3 *outLineDirection, Vector3 *outLinePoint, bint *outValid):
    cdef Vector3 direction, unitNormal1, unitNormal2, factor1, factor2, point
    cdef double h1, h2, dot, c1, c2, invDotSquared
    normalizeVec3(&unitNormal1, firstPlaneNormal)
    normalizeVec3(&unitNormal2, secondPlaneNormal)
    crossVec3(&direction, firstPlaneNormal, secondPlaneNormal)
    if lengthVec3(&direction) > 1e-6:
        h1 = dotVec3(firstPlaneNormal, firstPlanePoint)
        h2 = dotVec3(secondPlaneNormal, secondPlanePoint)
        dot = dotVec3(firstPlaneNormal, secondPlaneNormal)
        invDotSquared = (1 - dot ** 2)
        c1 = (h1 - h2 * dot)/invDotSquared
        c2 = (h2 - h1 * dot)/invDotSquared
        scaleVec3(&factor1, firstPlaneNormal, c1)
        scaleVec3(&factor2, secondPlaneNormal, c2)
        addVec3(&point, &factor1, &factor2)
        outLineDirection[0] = direction
        outLinePoint[0] = point
        outValid[0] = True
    else:
        outLineDirection[0] = Vector3(0,0,0)
        outLinePoint[0] = Vector3(0,0,0)
        outValid[0] = False

def intersectPlanePlaneList(Py_ssize_t amount,
                            VirtualVector3DList firstPlanePointList,
                            VirtualVector3DList firstPlaneNormalList,
                            VirtualVector3DList secondPlanePointList,
                            VirtualVector3DList secondPlaneNormalList):
    cdef Vector3DList lineDirectionList = Vector3DList(length = amount)
    cdef Vector3DList linePointList = Vector3DList(length = amount)
    cdef BooleanList validList = BooleanList(length = amount)
    cdef Vector3 lineDirection, linePoint
    cdef bint valid
    cdef Py_ssize_t i
    for i in range(amount):
        intersectPlanePlane(firstPlanePointList.get(i), firstPlaneNormalList.get(i),
        secondPlanePointList.get(i), secondPlaneNormalList.get(i),
        &lineDirection, &linePoint, &valid)
        lineDirectionList.data[i] = lineDirection
        linePointList.data[i] = linePoint
        validList.data[i] = valid
    return lineDirectionList, linePointList, validList

def intersectPlanePlaneSingle(firstPlanePoint,
                            firstPlaneNormal,
                            secondPlanePoint,
                            secondPlaneNormal):
    cdef Vector3 _firstPlanePoint = toVector3(firstPlanePoint)
    cdef Vector3 _firstPlaneNormal = toVector3(firstPlaneNormal)
    cdef Vector3 _secondPlanePoint = toVector3(secondPlanePoint)
    cdef Vector3 _secondPlaneNormal = toVector3(secondPlaneNormal)
    cdef Vector3 lineDirection, linePoint
    cdef bint valid
    intersectPlanePlane(&_firstPlanePoint, &_firstPlaneNormal,
    &_secondPlanePoint, &_secondPlaneNormal,
    &lineDirection, &linePoint, &valid)
    return toPyVector3(&lineDirection), toPyVector3(&linePoint), valid

cdef intersectSpherePlane(Vector3 *sphereCenter, double sphereRadius,
                        Vector3 *planePoint, Vector3 *planeNormal,
                        Vector3 *outCircleCenter, double *outCircleRadius, bint *outValid):
    cdef Vector3 direction, unitNormal, scaledNormal, center
    cdef double radius, distance
    normalizeVec3(&unitNormal, planeNormal)
    subVec3(&direction, sphereCenter, planePoint)
    distance = dotVec3(&direction, &unitNormal)
    if abs(distance) < sphereRadius:
        radius = sqrt(sphereRadius * sphereRadius - distance * distance)
        scaleVec3(&scaledNormal, &unitNormal, -distance)
        addVec3(&center, sphereCenter, &scaledNormal)
        outCircleCenter[0] = center
        outCircleRadius[0] = radius
        outValid[0] = True
    else:
        outCircleCenter[0] = Vector3(0,0,0)
        outCircleRadius[0] = 0
        outValid[0] = False

def intersectSpherePlaneList(Py_ssize_t amount,
                            VirtualVector3DList sphereCenterList,
                            VirtualDoubleList sphereRadiusList,
                            VirtualVector3DList planePointList,
                            VirtualVector3DList planeNormalList):
    cdef Vector3DList circleCenterList = Vector3DList(length = amount)
    cdef DoubleList circleRadiusList = DoubleList(length = amount)
    cdef BooleanList validList = BooleanList(length = amount)
    cdef Vector3 circleCenter
    cdef double circleRadius
    cdef bint valid
    cdef Py_ssize_t i
    for i in range(amount):
        intersectSpherePlane(sphereCenterList.get(i), sphereRadiusList.get(i),
        planePointList.get(i), planeNormalList.get(i),
        &circleCenter, &circleRadius, &valid)
        circleCenterList.data[i] = circleCenter
        circleRadiusList.data[i] = circleRadius
        validList.data[i] = valid
    return circleCenterList, circleRadiusList, validList

def intersectSpherePlaneSingle(sphereCenter,
                                sphereRadius,
                                planePoint,
                                planeNormal):
    cdef Vector3 _sphereCenter = toVector3(sphereCenter)
    cdef Vector3 _planePoint = toVector3(planePoint)
    cdef Vector3 _planeNormal = toVector3(planeNormal)
    cdef Vector3 circleCenter
    cdef double circleRadius
    cdef bint valid
    intersectSpherePlane(&_sphereCenter, sphereRadius,
    &_planePoint, &_planeNormal,
    &circleCenter, &circleRadius, &valid)
    return toPyVector3(&circleCenter), circleRadius, valid

cdef intersectSphereSphere(Vector3 *firstSphereCenter, double firstSphereRadius,
                            Vector3 *secondSphereCenter, double secondSphereRadius,
                            Vector3 *outCircleCenter, Vector3 *outCircleNormal,
                            double *outCircleRadius, bint *outValid):
    cdef Vector3 direction, scaledDirection, center
    cdef double distance, r1, r2, h, r
    subVec3(&direction, secondSphereCenter, firstSphereCenter)
    distance = lengthVec3(&direction)
    r1 = firstSphereRadius
    r2 = secondSphereRadius
    if (distance <= (r1 + r2)) and ((distance + min(r1, r2)) >= max(r1, r2)) and (distance != 0):
        h = 0.5 + (r1 * r1 - r2 * r2)/(2 * distance * distance)
        scaleVec3(&scaledDirection, &direction, h)
        addVec3(&center, firstSphereCenter, &scaledDirection)
        r = sqrt(r1 * r1 - h * h * distance * distance)
        outCircleCenter[0] = center
        outCircleNormal[0] = direction
        outCircleRadius[0] = r
        outValid[0] = True
    else:
        outCircleCenter[0] = Vector3(0,0,0)
        outCircleNormal[0] = Vector3(0,0,0)
        outCircleRadius[0] = 0
        outValid[0] = False

def intersectSphereSphereList(Py_ssize_t amount,
                            VirtualVector3DList firstSphereCenterList,
                            VirtualDoubleList firstSphereRadiusList,
                            VirtualVector3DList secondSphereCenterList,
                            VirtualDoubleList secondSphereRadiusList):
    cdef Vector3DList circleCenterList = Vector3DList(length = amount)
    cdef Vector3DList circleNormalList = Vector3DList(length = amount)
    cdef DoubleList circleRadiusList = DoubleList(length = amount)
    cdef BooleanList validList = BooleanList(length = amount)
    cdef Vector3 circleCenter, circleNormal
    cdef double circleRadius
    cdef bint valid
    cdef Py_ssize_t i
    for i in range(amount):
        intersectSphereSphere(firstSphereCenterList.get(i), firstSphereRadiusList.get(i),
        secondSphereCenterList.get(i), secondSphereRadiusList.get(i),
        &circleCenter, &circleNormal, &circleRadius, &valid)
        circleCenterList.data[i] = circleCenter
        circleNormalList.data[i] = circleNormal
        circleRadiusList.data[i] = circleRadius
        validList.data[i] = valid
    return circleCenterList, circleNormalList, circleRadiusList, validList

def intersectSphereSphereSingle(firstSphereCenter,
                                firstSphereRadius,
                                secondSphereCenter,
                                secondSphereRadius):
    cdef Vector3 _firstSphereCenter = toVector3(firstSphereCenter)
    cdef Vector3 _secondSphereCenter = toVector3(secondSphereCenter)
    cdef Vector3 circleCenter, circleNormal
    cdef double circleRadius
    cdef bint valid
    intersectSphereSphere(&_firstSphereCenter, firstSphereRadius,
    &_secondSphereCenter, secondSphereRadius,
    &circleCenter, &circleNormal, &circleRadius, &valid)
    return toPyVector3(&circleCenter), toPyVector3(&circleNormal), circleRadius, valid

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
