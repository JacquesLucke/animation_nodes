cimport cython
from . number cimport lerpFloat
from . vector cimport crossVec3, scaleVec3_Inplace, scaleVec3, lengthVec3, angleVec3, projectOnCenterPlaneVec3, normalizeVec3, dotVec3, subVec3
from libc.math cimport cos, sin, sqrt, acos, fabs

cdef void setUnitQuaternion(Quaternion *q):
    q.x, q.y, q.z, q.w = 0, 0, 0, 1

cdef void multQuat(Quaternion *target, Quaternion *q1, Quaternion *q2):
    target.w = q1.w * q2.w - q1.x * q2.x - q1.y * q2.y - q1.z * q2.z
    target.x = q1.w * q2.x + q1.x * q2.w + q1.y * q2.z - q1.z * q2.y
    target.y = q1.w * q2.y + q1.y * q2.w + q1.z * q2.x - q1.x * q2.z
    target.z = q1.w * q2.z + q1.z * q2.w + q1.x * q2.y - q1.y * q2.x

cdef void rotVec3ByQuat(Vector3 *target, Vector3 *v, Quaternion *q):
    # https://blog.molecular-matters.com/2013/05/24/a-faster-quaternion-vector-multiplication/
    cdef Vector3 _q = Vector3(q.x, q.y, q.z)

    cdef Vector3 t
    crossVec3(&t, &_q, v)
    scaleVec3_Inplace(&t, 2)

    cdef Vector3 p
    crossVec3(&p, &_q, &t)

    target.x = v.x + q.w * t.x + p.x
    target.y = v.y + q.w * t.y + p.y
    target.z = v.z + q.w * t.z + p.z

@cython.cdivision(True)
cdef void quaternionNormalize_InPlace(Quaternion *q):
    cdef float length = sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z)
    if length != 0:
        q.w /= length
        q.x /= length
        q.y /= length
        q.z /= length

# https://gitlab.com/bztsrc/slerp-opt
cdef void mixQuat(Quaternion* target, Quaternion* x, Quaternion* y, float factor):
    cdef float a = 1 - factor
    cdef float b = factor
    cdef float d = x.x * y.x + x.y * y.y + x.z * y.z + x.w * y.w
    cdef float c = fabs(d)

    if c < 0.999:
        c = acos(c)
        b = 1 / sin(c)
        a = sin(a * c) * b
        b *= sin(factor * c)
        if d < 0:
            b = -b

    target.w = x.w * a + y.w * b
    target.x = x.x * a + y.x * b
    target.y = x.y * a + y.y * b
    target.z = x.z * a + y.z * b
