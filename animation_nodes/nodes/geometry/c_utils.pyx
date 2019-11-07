import cython
from libc.math cimport sqrt
from ... math cimport ( Vector3, dotVec3, scaleVec3, normalizeVec3,
    addVec3, subVec3, crossVec3, lengthVec3, lengthSquaredVec3,
    distanceVec3, toVector3, toPyVector3)
from ... data_structures cimport (
    Vector3DList, DoubleList, VirtualDoubleList,
    VirtualVector3DList, BooleanList, CharList)

# Line-Line Intersection
################################################

@cython.cdivision(True)
cdef intersect_LineLine(Vector3 *firstLineStart, Vector3 *firstLineEnd,
                        Vector3 *secondLineStart, Vector3 *secondLineEnd,
                        Vector3 *outFirstNearestPoint, Vector3 *outSecondNearestPoint,
                        double *outFirstParameter, double *outSecondParameter, char *outValid):
    cdef Vector3 direction1, direction2, normal, normal1, normal2, direction12, direction21
    cdef Vector3 scaledDirection1, scaledDirection2, nearestPointA, nearestPointB
    cdef double factor1, factor2
    subVec3(&direction1, firstLineEnd, firstLineStart)
    subVec3(&direction2, secondLineEnd, secondLineStart)
    crossVec3(&normal, &direction1, &direction2)
    if lengthVec3(&normal) < 1e-6:
        outFirstNearestPoint[0] = Vector3(0,0,0)
        outSecondNearestPoint[0] = Vector3(0,0,0)
        outFirstParameter[0] = 0
        outSecondParameter[0] = 0
        outValid[0] = False
        return

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

def intersect_LineLine_List(Py_ssize_t amount,
                            VirtualVector3DList firstLineStartList,
                            VirtualVector3DList firstLineEndList,
                            VirtualVector3DList secondLineStartList,
                            VirtualVector3DList secondLineEndList):
    cdef Vector3DList firstNearestPointList = Vector3DList(length = amount)
    cdef Vector3DList secondNearestPointList = Vector3DList(length = amount)
    cdef DoubleList firstParameterList = DoubleList(length = amount)
    cdef DoubleList secondParameterList = DoubleList(length = amount)
    cdef BooleanList validList = BooleanList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        intersect_LineLine(firstLineStartList.get(i), firstLineEndList.get(i),
                           secondLineStartList.get(i), secondLineEndList.get(i),
                           firstNearestPointList.data + i, secondNearestPointList.data + i,
                           firstParameterList.data + i, secondParameterList.data + i,
                           validList.data + i)
    return (firstNearestPointList, secondNearestPointList,
            firstParameterList, secondParameterList, validList)

def intersect_LineLine_Single(firstLineStart,
                              firstLineEnd,
                              secondLineStart,
                              secondLineEnd):
    cdef Vector3 _firstLineStart = toVector3(firstLineStart)
    cdef Vector3 _firstLineEnd = toVector3(firstLineEnd)
    cdef Vector3 _secondLineStart = toVector3(secondLineStart)
    cdef Vector3 _secondLineEnd = toVector3(secondLineEnd)
    cdef Vector3 firstNearestPoint, secondNearestPoint
    cdef double firstParameter, secondParameter
    cdef char valid
    intersect_LineLine(&_firstLineStart, &_firstLineEnd, &_secondLineStart, &_secondLineEnd,
                       &firstNearestPoint, &secondNearestPoint, &firstParameter, &secondParameter,
                       &valid)
    return (toPyVector3(&firstNearestPoint), toPyVector3(&secondNearestPoint),
            firstParameter, secondParameter, bool(valid))

# Line-Plane Intersection
################################################

@cython.cdivision(True)
cdef intersect_LinePlane(Vector3 *lineStart, Vector3 *lineEnd,
                         Vector3 *planePoint, Vector3 *planeNormal,
                         Vector3 *outIntersection, double *outParameter, char *outValid):
    cdef Vector3 direction, pointDirection, intersectionVector, intersection
    cdef double parameter, dot
    subVec3(&direction, lineEnd, lineStart)
    dot = dotVec3(planeNormal, &direction)
    if abs(dot) < 1e-6:
        outIntersection[0] = Vector3(0,0,0)
        outParameter[0] = 0
        outValid[0] = False
        return

    subVec3(&pointDirection, lineStart, planePoint)
    factor = -dotVec3(planeNormal, &pointDirection) / dot
    scaleVec3(&intersectionVector, &direction, factor)
    addVec3(&intersection, lineStart, &intersectionVector)

    outIntersection[0] = intersection
    outParameter[0] = factor
    outValid[0] = True

def intersect_LinePlane_List(Py_ssize_t amount,
                             VirtualVector3DList lineStartList,
                             VirtualVector3DList lineEndList,
                             VirtualVector3DList planePointList,
                             VirtualVector3DList planeNormalList):
    cdef Vector3DList intersectionList = Vector3DList(length = amount)
    cdef DoubleList parameterList = DoubleList(length = amount)
    cdef BooleanList validList = BooleanList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        intersect_LinePlane(lineStartList.get(i), lineEndList.get(i),
                            planePointList.get(i), planeNormalList.get(i),
                            intersectionList.data + i, parameterList.data + i,
                            validList.data + i)
    return intersectionList, parameterList, validList

def intersect_LinePlane_Single(lineStart,
                               lineEnd,
                               planePoint,
                               planeNormal):
    cdef Vector3 _lineStart = toVector3(lineStart)
    cdef Vector3 _lineEnd = toVector3(lineEnd)
    cdef Vector3 _planePoint = toVector3(planePoint)
    cdef Vector3 _planeNormal = toVector3(planeNormal)
    cdef Vector3 intersection
    cdef double parameter
    cdef char valid
    intersect_LinePlane(&_lineStart, &_lineEnd, &_planePoint, &_planeNormal,
                        &intersection, &parameter, &valid)
    return toPyVector3(&intersection), parameter, bool(valid)

# Line-Sphere Intersection
################################################

@cython.cdivision(True)
cdef intersect_LineSphere(Vector3 *lineStart, Vector3 *lineEnd,
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
    discriminant = b * b - 4 * a * c
    if discriminant < 0 or a == 0:
        outFirstIntersection[0] = Vector3(0,0,0)
        outSecondIntersection[0] = Vector3(0,0,0)
        outFirstParameter[0] = 0
        outSecondParameter[0] = 0
        outNumberOfIntersections[0] = 0
        return

    if discriminant < 1e-6:
        factor = (-b + sqrt(discriminant))/(2 * a)
        scaleVec3(&firstIntersection, &direction, factor)
        addVec3(&firstIntersection, lineStart, &firstIntersection)

        outFirstIntersection[0] = firstIntersection
        outSecondIntersection[0] = firstIntersection
        outFirstParameter[0] = factor
        outSecondParameter[0] = factor
        outNumberOfIntersections[0] = 1
        return

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

def intersect_LineSphere_List(Py_ssize_t amount,
                              VirtualVector3DList lineStartList,
                              VirtualVector3DList lineEndList,
                              VirtualVector3DList sphereCenterList,
                              VirtualDoubleList sphereRadiusList):
    cdef Vector3DList firstIntersectionList = Vector3DList(length = amount)
    cdef Vector3DList secondIntersectionList = Vector3DList(length = amount)
    cdef DoubleList firstParameterList = DoubleList(length = amount)
    cdef DoubleList secondParameterList = DoubleList(length = amount)
    cdef CharList numberOfIntersectionsList = CharList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        intersect_LineSphere(lineStartList.get(i), lineEndList.get(i),
                             sphereCenterList.get(i), sphereRadiusList.get(i),
                             firstIntersectionList.data + i, secondIntersectionList.data + i,
                             firstParameterList.data + i, secondParameterList.data + i,
                             numberOfIntersectionsList.data + i)
    return (firstIntersectionList, secondIntersectionList,
            firstParameterList, secondParameterList,
            numberOfIntersectionsList)

def intersect_LineSphere_Single(lineStart,
                                lineEnd,
                                sphereCenter,
                                sphereRadius):
    cdef Vector3 _lineStart = toVector3(lineStart)
    cdef Vector3 _lineEnd = toVector3(lineEnd)
    cdef Vector3 _sphereCenter = toVector3(sphereCenter)
    cdef Vector3 firstIntersection, secondIntersection
    cdef double firstParameter, secondParameter
    cdef char numberOfIntersections
    intersect_LineSphere(&_lineStart, &_lineEnd, &_sphereCenter, sphereRadius,
                         &firstIntersection, &secondIntersection,
                         &firstParameter,&secondParameter, &numberOfIntersections)
    return (toPyVector3(&firstIntersection), toPyVector3(&secondIntersection),
            firstParameter, secondParameter,
            numberOfIntersections)

# Plane-Plane Intersection
################################################

@cython.cdivision(True)
cdef intersect_PlanePlane(Vector3 *firstPlanePoint, Vector3 *firstPlaneNormal,
                          Vector3 *secondPlanePoint, Vector3 *secondPlaneNormal,
                          Vector3 *outLineDirection, Vector3 *outLinePoint, char *outValid):
    cdef Vector3 direction, unitNormal1, unitNormal2, factor1, factor2, point
    cdef double h1, h2, dot, c1, c2, invDotSquared
    normalizeVec3(&unitNormal1, firstPlaneNormal)
    normalizeVec3(&unitNormal2, secondPlaneNormal)
    crossVec3(&direction, firstPlaneNormal, secondPlaneNormal)
    if lengthVec3(&direction) < 1e-6:
        outLineDirection[0] = Vector3(0,0,0)
        outLinePoint[0] = Vector3(0,0,0)
        outValid[0] = False
        return

    h1 = dotVec3(firstPlaneNormal, firstPlanePoint)
    h2 = dotVec3(secondPlaneNormal, secondPlanePoint)
    dot = dotVec3(firstPlaneNormal, secondPlaneNormal)
    invDotSquared = (1 - dot * dot)
    c1 = (h1 - h2 * dot)/invDotSquared
    c2 = (h2 - h1 * dot)/invDotSquared
    scaleVec3(&factor1, firstPlaneNormal, c1)
    scaleVec3(&factor2, secondPlaneNormal, c2)
    addVec3(&point, &factor1, &factor2)

    outLineDirection[0] = direction
    outLinePoint[0] = point
    outValid[0] = True

def intersect_PlanePlane_List(Py_ssize_t amount,
                              VirtualVector3DList firstPlanePointList,
                              VirtualVector3DList firstPlaneNormalList,
                              VirtualVector3DList secondPlanePointList,
                              VirtualVector3DList secondPlaneNormalList):
    cdef Vector3DList lineDirectionList = Vector3DList(length = amount)
    cdef Vector3DList linePointList = Vector3DList(length = amount)
    cdef BooleanList validList = BooleanList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        intersect_PlanePlane(firstPlanePointList.get(i), firstPlaneNormalList.get(i),
                             secondPlanePointList.get(i), secondPlaneNormalList.get(i),
                             lineDirectionList.data + i, linePointList.data + i,
                             validList.data + i)
    return lineDirectionList, linePointList, validList

def intersect_PlanePlane_Single(firstPlanePoint,
                                firstPlaneNormal,
                                secondPlanePoint,
                                secondPlaneNormal):
    cdef Vector3 _firstPlanePoint = toVector3(firstPlanePoint)
    cdef Vector3 _firstPlaneNormal = toVector3(firstPlaneNormal)
    cdef Vector3 _secondPlanePoint = toVector3(secondPlanePoint)
    cdef Vector3 _secondPlaneNormal = toVector3(secondPlaneNormal)
    cdef Vector3 lineDirection, linePoint
    cdef char valid
    intersect_PlanePlane(&_firstPlanePoint, &_firstPlaneNormal,
                         &_secondPlanePoint, &_secondPlaneNormal,
                         &lineDirection, &linePoint, &valid)
    return toPyVector3(&lineDirection), toPyVector3(&linePoint), bool(valid)

# Sphere-Plane Intersection
################################################

cdef intersect_SpherePlane(Vector3 *sphereCenter, double sphereRadius,
                           Vector3 *planePoint, Vector3 *planeNormal,
                           Vector3 *outCircleCenter, double *outCircleRadius, char *outValid):
    cdef Vector3 direction, unitNormal, scaledNormal, center
    cdef double radius, distance
    normalizeVec3(&unitNormal, planeNormal)
    subVec3(&direction, sphereCenter, planePoint)
    distance = dotVec3(&direction, &unitNormal)
    if abs(distance) > sphereRadius:
        outCircleCenter[0] = Vector3(0,0,0)
        outCircleRadius[0] = 0
        outValid[0] = False
        return

    radius = sqrt(sphereRadius * sphereRadius - distance * distance)
    scaleVec3(&scaledNormal, &unitNormal, -distance)
    addVec3(&center, sphereCenter, &scaledNormal)

    outCircleCenter[0] = center
    outCircleRadius[0] = radius
    outValid[0] = True

def intersect_SpherePlane_List(Py_ssize_t amount,
                               VirtualVector3DList sphereCenterList,
                               VirtualDoubleList sphereRadiusList,
                               VirtualVector3DList planePointList,
                               VirtualVector3DList planeNormalList):
    cdef Vector3DList circleCenterList = Vector3DList(length = amount)
    cdef DoubleList circleRadiusList = DoubleList(length = amount)
    cdef BooleanList validList = BooleanList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        intersect_SpherePlane(sphereCenterList.get(i), sphereRadiusList.get(i),
                              planePointList.get(i), planeNormalList.get(i),
                              circleCenterList.data + i, circleRadiusList.data + i,
                              validList.data + i)
    return circleCenterList, circleRadiusList, validList

def intersect_SpherePlane_Single(sphereCenter,
                                 sphereRadius,
                                 planePoint,
                                 planeNormal):
    cdef Vector3 _sphereCenter = toVector3(sphereCenter)
    cdef Vector3 _planePoint = toVector3(planePoint)
    cdef Vector3 _planeNormal = toVector3(planeNormal)
    cdef Vector3 circleCenter
    cdef double circleRadius
    cdef char valid
    intersect_SpherePlane(&_sphereCenter, sphereRadius,
                          &_planePoint, &_planeNormal,
                          &circleCenter, &circleRadius, &valid)
    return toPyVector3(&circleCenter), circleRadius, bool(valid)

# Sphere-Sphere Intersection
################################################

@cython.cdivision(True)
cdef intersect_SphereSphere(Vector3 *firstSphereCenter, double firstSphereRadius,
                            Vector3 *secondSphereCenter, double secondSphereRadius,
                            Vector3 *outCircleCenter, Vector3 *outCircleNormal,
                            double *outCircleRadius, char *outValid):
    cdef Vector3 direction, scaledDirection, center
    cdef double distance, r1, r2, h, r
    subVec3(&direction, secondSphereCenter, firstSphereCenter)
    distance = lengthVec3(&direction)
    r1 = firstSphereRadius
    r2 = secondSphereRadius
    if (distance > (r1 + r2)) or ((distance + min(r1, r2)) < max(r1, r2)) or (distance == 0):
        outCircleCenter[0] = Vector3(0,0,0)
        outCircleNormal[0] = Vector3(0,0,0)
        outCircleRadius[0] = 0
        outValid[0] = False
        return

    h = 0.5 + (r1 * r1 - r2 * r2)/(2 * distance * distance)
    scaleVec3(&scaledDirection, &direction, h)
    addVec3(&center, firstSphereCenter, &scaledDirection)
    r = sqrt(r1 * r1 - h * h * distance * distance)

    outCircleCenter[0] = center
    outCircleNormal[0] = direction
    outCircleRadius[0] = r
    outValid[0] = True

def intersect_SphereSphere_List(Py_ssize_t amount,
                                VirtualVector3DList firstSphereCenterList,
                                VirtualDoubleList firstSphereRadiusList,
                                VirtualVector3DList secondSphereCenterList,
                                VirtualDoubleList secondSphereRadiusList):
    cdef Vector3DList circleCenterList = Vector3DList(length = amount)
    cdef Vector3DList circleNormalList = Vector3DList(length = amount)
    cdef DoubleList circleRadiusList = DoubleList(length = amount)
    cdef BooleanList validList = BooleanList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        intersect_SphereSphere(firstSphereCenterList.get(i), firstSphereRadiusList.get(i),
                               secondSphereCenterList.get(i), secondSphereRadiusList.get(i),
                               circleCenterList.data + i, circleNormalList.data + i,
                               circleRadiusList.data + i, validList.data + i)
    return circleCenterList, circleNormalList, circleRadiusList, validList

def intersect_SphereSphere_Single(firstSphereCenter,
                                  firstSphereRadius,
                                  secondSphereCenter,
                                  secondSphereRadius):
    cdef Vector3 _firstSphereCenter = toVector3(firstSphereCenter)
    cdef Vector3 _secondSphereCenter = toVector3(secondSphereCenter)
    cdef Vector3 circleCenter, circleNormal
    cdef double circleRadius
    cdef char valid
    intersect_SphereSphere(&_firstSphereCenter, firstSphereRadius,
                           &_secondSphereCenter, secondSphereRadius,
                           &circleCenter, &circleNormal, &circleRadius, &valid)
    return toPyVector3(&circleCenter), toPyVector3(&circleNormal), circleRadius, bool(valid)

# Project Point On Line
################################################

@cython.cdivision(True)
cdef project_PointOnLine(Vector3 *lineStart, Vector3 *lineEnd, Vector3 *point,
                         Vector3 *outProjection, double *outParameter, double *outDistance):
    cdef Vector3 direction1, direction2, unitDirection, projVector, projection
    cdef double factor, length, parameter, distance
    subVec3(&direction1, lineEnd, lineStart)
    subVec3(&direction2, point, lineStart)
    normalizeVec3(&unitDirection, &direction1)
    factor = dotVec3(&direction2, &unitDirection)
    scaleVec3(&projVector, &unitDirection, factor)
    addVec3(&projection, lineStart, &projVector)
    length = lengthVec3(&direction1)
    parameter = factor / length if length != 0 else 0
    distance = distanceVec3(&projVector, point)

    outProjection[0] = projection
    outParameter[0] = parameter
    outDistance[0] = distance

def project_PointOnLine_List(Py_ssize_t amount,
                             VirtualVector3DList lineStartList,
                             VirtualVector3DList lineEndList,
                             VirtualVector3DList pointList):
    cdef Vector3DList projectionList = Vector3DList(length = amount)
    cdef DoubleList parameterList = DoubleList(length = amount)
    cdef DoubleList distanceList = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        project_PointOnLine(lineStartList.get(i), lineEndList.get(i), pointList.get(i),
                           projectionList.data + i, parameterList.data + i,
                           distanceList.data + i)
    return projectionList, parameterList, distanceList

def project_PointOnLine_Single(lineStart,
                               lineEnd,
                               point):
    cdef Vector3 _lineStart = toVector3(lineStart)
    cdef Vector3 _lineEnd = toVector3(lineEnd)
    cdef Vector3 _point = toVector3(point)
    cdef Vector3 projection
    cdef double parameter, distance
    project_PointOnLine(&_lineStart, &_lineEnd, &_point, &projection, &parameter, &distance)
    return toPyVector3(&projection), parameter, distance

# Project Point On Line
################################################

cdef project_PointOnPlane(Vector3 *planePoint, Vector3 *planeNormal, Vector3 *point,
                          Vector3 *outProjection, double *outDistance):
    cdef Vector3 direction, unitNormal, projVector, projection
    cdef double distance
    subVec3(&direction, point, planePoint)
    normalizeVec3(&unitNormal, planeNormal)
    distance = dotVec3(&direction, &unitNormal)
    scaleVec3(&projVector, &unitNormal, -distance)
    addVec3(&projection, point, &projVector)

    outProjection[0] = projection
    outDistance[0] = distance

def project_PointOnPlane_List(Py_ssize_t amount,
                              VirtualVector3DList planePointList,
                              VirtualVector3DList planeNormalList,
                              VirtualVector3DList pointList):
    cdef Vector3DList projectionList = Vector3DList(length = amount)
    cdef DoubleList distanceList = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        project_PointOnPlane(planePointList.get(i), planeNormalList.get(i), pointList.get(i),
                             projectionList.data + i, distanceList.data + i)
    return projectionList, distanceList

def project_PointOnPlane_Single(planePoint,
                                planeNormal,
                                point):
    cdef Vector3 _planePoint = toVector3(planePoint)
    cdef Vector3 _planeNormal = toVector3(planeNormal)
    cdef Vector3 _point = toVector3(point)
    cdef Vector3 projection
    cdef double distance
    project_PointOnPlane(&_planePoint, &_planeNormal, &_point,
                         &projection, &distance)
    return toPyVector3(&projection), distance
