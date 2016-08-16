from libc.math cimport sqrt

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
    return sqrt((a.x - b.x) ** 2
              + (a.y - b.y) ** 2
              + (a.z - b.z) ** 2)

cdef float distanceSquaredVec3(Vector3* a, Vector3* b):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2

cdef void transformVec3(Vector3* target, Vector3* v, Matrix4* m):
    cdef float newX, newY, newZ
    newX = v.x * m.a11 + v.y * m.a12 + v.z * m.a13 + m.a14
    newY = v.x * m.a21 + v.y * m.a22 + v.z * m.a23 + m.a24
    newZ = v.x * m.a31 + v.y * m.a32 + v.z * m.a33 + m.a34
    target.x = newX
    target.y = newY
    target.z = newZ

cdef float dotVec3(Vector3* a, Vector3* b):
    return a.x * b.x + a.y * b.y + a.z * b.z

cdef void crossVec3(Vector3* result, Vector3* a, Vector3* b):
    result.x = a.y * b.z - a.z * b.y
    result.y = a.z * b.x - a.x * b.z
    result.z = a.x * b.y - a.y * b.x
