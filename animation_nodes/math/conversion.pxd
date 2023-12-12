from . color cimport Color
from . euler cimport Euler3
from . quaternion cimport Quaternion
from . vector cimport Vector2, Vector3, Vector4, Int2
from . matrix cimport Matrix3, Matrix4, Matrix3_or_Matrix4

cdef Matrix4 toMatrix4(value) except *
cdef setMatrix4(Matrix4* m, value)
cdef toPyMatrix4(Matrix4* m)

cdef toPyMatrix3(Matrix3* m)

cdef Vector2 toVector2(value) except *
cdef setVector2(Vector2* v, value)
cdef toPyVector2(Vector2* v)

cdef Vector3 toVector3(value) except *
cdef setVector3(Vector3* v, value)
cdef toPyVector3(Vector3* v)

cdef Vector4 toVector4(value) except *
cdef setVector4(Vector4* v, value)
cdef toPyVector4(Vector4* v)

cdef Int2 toInt2(value) except *
cdef setInt2(Int2* v, value)
cdef toPyInt2(Int2* v)

cdef Euler3 toEuler3(value) except *
cdef setEuler3(Euler3* e, value)
cdef toPyEuler3(Euler3* e)

cdef Quaternion toQuaternion(value) except *
cdef setQuaternion(Quaternion* q, value)
cdef toPyQuaternion(Quaternion* q)

cdef Color toColor(value) except *
cdef setColor(Color* c, value)
cdef toPyColor(Color* c)
