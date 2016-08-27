cdef struct Vector3:
    float x, y, z

cdef float lengthVec3(Vector3* v)
cdef void scaleVec3(Vector3* v, float factor)
cdef void addVec3(Vector3* target, Vector3* a, Vector3* b)
cdef void subVec3(Vector3* target, Vector3* a, Vector3* b)
cdef void mixVec3(Vector3* target, Vector3* a, Vector3* b, float factor)
cdef void crossVec3(Vector3* result, Vector3* a, Vector3* b)
cdef float dotVec3(Vector3* a, Vector3* b)

cdef void normalizeVec3(Vector3* v)
cdef float distanceVec3(Vector3* a, Vector3* b)
cdef float distanceSquaredVec3(Vector3* a, Vector3* b)
