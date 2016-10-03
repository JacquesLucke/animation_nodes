import cython
from libc.math cimport sqrt

if sizeof(Vector3) != 12:
    raise MemoryError("The compiler added padding to the Vector3 struct")

cdef void scaleVec3(Vector3* v, float factor):
    v.x *= factor
    v.y *= factor
    v.z *= factor

cdef float lengthVec3(Vector3* v):
    return sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)

cdef void addVec3(Vector3* target, Vector3* a, Vector3* b):
    target.x = a.x + b.x
    target.y = a.y + b.y
    target.z = a.z + b.z

cdef void subVec3(Vector3* target, Vector3* a, Vector3* b):
    target.x = a.x - b.x
    target.y = a.y - b.y
    target.z = a.z - b.z

cdef void mixVec3(Vector3* target, Vector3* a, Vector3* b, float factor):
    cdef float newX, newY, newZ
    newX = a.x * (1 - factor) + b.x * factor
    newY = a.y * (1 - factor) + b.y * factor
    newZ = a.z * (1 - factor) + b.z * factor
    target.x = newX
    target.y = newY
    target.z = newZ

@cython.cdivision(True)
cdef void normalizeVec3(Vector3* v):
    cdef float length = sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)
    if length != 0:
        v.x /= length
        v.y /= length
        v.z /= length
    else:
        v.x = 0
        v.y = 0
        v.z = 0

cdef float distanceVec3(Vector3* a, Vector3* b):
    return sqrt(distanceSquaredVec3(a, b))

cdef float distanceSquaredVec3(Vector3* a, Vector3* b):
    cdef:
        float diff1 = (a.x - b.x)
        float diff2 = (a.y - b.y)
        float diff3 = (a.z - b.z)
    return diff1 * diff1 + diff2 * diff2 + diff3 * diff3

cdef float dotVec3(Vector3* a, Vector3* b):
    return a.x * b.x + a.y * b.y + a.z * b.z

cdef void crossVec3(Vector3* result, Vector3* a, Vector3* b):
    result.x = a.y * b.z - a.z * b.y
    result.y = a.z * b.x - a.x * b.z
    result.z = a.x * b.y - a.y * b.x
