from . vector cimport Vector3
from . matrix cimport Matrix4

cdef Matrix4 toMatrix4(value) except *
cdef setMatrix4(Matrix4* m, value)
cdef toPyMatrix4(Matrix4* m)

cdef Vector3 toVector3(value) except *
cdef setVector3(Vector3* v, value)
cdef toPyVector3(Vector3* v)
