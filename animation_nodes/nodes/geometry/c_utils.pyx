from ... math cimport ( Vector3, dotVec3, scaleVec3,
    addVec3, subVec3, crossVec3, lengthVec3)
from ... data_structures cimport (
    Vector3DList, DoubleList,
    VirtualVector3DList, BooleanList)

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
