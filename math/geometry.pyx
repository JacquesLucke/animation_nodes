cimport cython
from . base_operations cimport *

@cython.cdivision(True)
cdef float findNearestLineParameter(Vector3* lineStart, Vector3* lineDirection, Vector3* point):
    cdef float directionLength = lengthVec3(lineDirection)
    if directionLength == 0: return 0.0

    cdef Vector3 normalizedLineDirection = lineDirection[0]
    scaleVec3(&normalizedLineDirection, 1 / directionLength)

    cdef Vector3 pointDifference
    subVec3(&pointDifference, point, lineStart)
    return dotVec3(&normalizedLineDirection, &pointDifference) / directionLength
