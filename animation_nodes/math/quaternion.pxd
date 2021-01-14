from . vector cimport Vector3

ctypedef struct Quaternion:
    float x, y, z, w

cdef void setUnitQuaternion(Quaternion *q)
cdef void multQuat(Quaternion *target, Quaternion *q1, Quaternion *q2)
cdef void rotVec3ByQuat(Vector3 *target, Vector3 *v, Quaternion *q)
cdef void quaternionNormalize_InPlace(Quaternion *q)
cdef void mixQuat(Quaternion* target, Quaternion* x, Quaternion* y, float factor)
