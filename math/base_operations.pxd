from . ctypes cimport Vector3, Matrix4

cdef void addVec3(Vector3* target, Vector3* a, Vector3* b)
cdef void transformVec3(Vector3* target, Vector3* v, Matrix4* m)
cdef double distanceVec3(Vector3* a, Vector3* b)
cdef void mixVec3(Vector3* target, Vector3* a, Vector3* b, float factor)
