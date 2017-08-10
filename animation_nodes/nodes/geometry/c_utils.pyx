from ... math cimport Vector3, dotVec3, scaleVec3, addVec3, subVec3
from ... data_structures cimport (
    Vector3DList, DoubleList,
    VirtualVector3DList, BooleanList)

def IntersectLinePlane(Py_ssize_t amount,
                      VirtualVector3DList lineStart,
                      VirtualVector3DList lineEnd,
                      VirtualVector3DList planePoint,
                      VirtualVector3DList planeNormal):
    cdef Vector3DList intersection = Vector3DList(length = amount)
    cdef BooleanList valid = BooleanList(length = amount)
    cdef DoubleList parameter = DoubleList(length = amount)
    cdef Vector3 direction
    cdef Vector3 pointDirection
    cdef double factor
    cdef Vector3 _intersection
    cdef Vector3 intersectionVector
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
