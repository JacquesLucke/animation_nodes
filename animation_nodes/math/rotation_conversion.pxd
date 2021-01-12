from .. data_structures.lists.base_lists cimport EulerList, Matrix4x4List, QuaternionList
from . matrix cimport Matrix3_or_Matrix4, Matrix4
from . euler cimport Euler3
from . quaternion cimport Quaternion
from . vector cimport Vector3

cdef matrixToEuler(Euler3* target, Matrix3_or_Matrix4* m)
cdef void normalizedAxisAngleToMatrix(Matrix3_or_Matrix4* m, Vector3* axis, float angle)
cdef void normalizedAxisCosAngleToMatrix(Matrix3_or_Matrix4* m, Vector3* axis, float cosAngle)
cdef euler3ToQuaternion(Quaternion* q, Euler3 *e)
cdef quaternionToMatrix4(Matrix4 *m, Quaternion *q)
cdef quaternionToEuler3(Euler3 *e, Quaternion *q)
cdef void quatFromAxisAngle(Quaternion *q, Vector3 *axis, float angle)
cdef void quatToAxisAngle(Vector3 *v, float *a, Quaternion *q)
