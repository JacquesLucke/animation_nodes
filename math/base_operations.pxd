from . cimport Vector3, Matrix4

cdef void transformVec3(Vector3* target, Vector3* v, Matrix4* m)
