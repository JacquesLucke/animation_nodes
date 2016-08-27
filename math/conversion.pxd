from . cimport Matrix4, Vector3

cdef toMatrix4(Matrix4* m, value)
cdef toVector3(Vector3* v, value)
cdef toPyVector(Vector3* v)
