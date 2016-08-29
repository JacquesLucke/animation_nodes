cimport cython
from . cimport subVec3, scaleVec3, lengthVec3, dotVec3, Vector3, distanceVec3

@cython.cdivision(True)
cdef float findNearestLineParameter(Vector3* lineStart, Vector3* lineDirection, Vector3* point):
    cdef float directionLength = lengthVec3(lineDirection)
    if directionLength == 0: return 0.0

    cdef Vector3 normalizedLineDirection = lineDirection[0]
    scaleVec3(&normalizedLineDirection, 1 / directionLength)

    cdef Vector3 pointDifference
    subVec3(&pointDifference, point, lineStart)
    return dotVec3(&normalizedLineDirection, &pointDifference) / directionLength

cdef double distancePointToPlane(Vector3* planePoint, Vector3* planeNormal, Vector3* point):
    cdef Vector3 projection
    projectPointOnPlane(planePoint, planeNormal, point, &projection)
    return distanceVec3(point, &projection)

@cython.cdivision(True)
cdef void projectPointOnPlane(Vector3* planePoint, Vector3* planeNormal, Vector3* point, Vector3* projection):
    cdef:
        Vector3 diff
        float sb, sn, sd

    subVec3(&diff, planePoint, point)
    sn = -dotVec3(planeNormal, &diff)
    sd = dotVec3(planeNormal, planeNormal)
    if sd == 0: sd = 1
    sb = sn / sd
    projection.x = point.x + sb * planeNormal.x
    projection.y = point.y + sb * planeNormal.y
    projection.z = point.z + sb * planeNormal.z
