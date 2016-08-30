from . cimport Matrix4, Vector3

cdef setMatrix4(Matrix4* m, value)
cdef toPyMatrix(Matrix4* m)

cdef setVector3(Vector3* v, value)
cdef toPyVector(Vector3* v)
