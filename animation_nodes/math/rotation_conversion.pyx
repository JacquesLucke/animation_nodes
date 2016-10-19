from libc.math cimport atan2, sqrt
from . matrix cimport normalizeMatrix_3x3_Part

# Matrix to Euler
################################################################

def matrix4x4ListToEulerList(Matrix4x4List matrices):
    cdef EulerList rotations = EulerList(length = matrices.length)
    cdef long i
    for i in range(rotations.length):
        matrixToEuler(rotations.data + i, matrices.data + i)
    return rotations

cdef matrixToEuler(Euler3* target, Matrix3_or_Matrix4* m):
    target.order = 0
    target.x = atan2(m.a32, m.a33)
    target.y = atan2(-m.a31, sqrt(m.a32 * m.a32 + m.a33 * m.a33))
    target.z = atan2(m.a21, m.a11)

# Matrix to Quaternion
################################################################

def matrix4x4ListToQuaternionList(Matrix4x4List matrices):
    cdef QuaternionList quaternions = QuaternionList(length = matrices.length)
    cdef long i
    for i in range(quaternions.length):
        matrixToQuaternion(quaternions.data + i, matrices.data + i)
    return quaternions

cdef void matrixToQuaternion(Quaternion* target, Matrix3_or_Matrix4* m):
    cdef Matrix3_or_Matrix4 _m
    normalizeMatrix_3x3_Part(&_m, m)
    normalizedMatrixToQuaternion(target, &_m)

cdef void normalizedMatrixToQuaternion(Quaternion* q, Matrix3_or_Matrix4* m):
    cdef float trace, s

    trace = 0.25 * (1.0 + m.a11 + m.a22 + m.a33)
    if trace > 0.0001:
        s = sqrt(trace)
        q.w = s
        s = 1.0 / (4.0 * s)
        q.x = -s * (m.a23 - m.a32)
        q.y = -s * (m.a31 - m.a13)
        q.z = -s * (m.a12 - m.a21)
    elif m.a11 > m.a22 and m.a11 > m.a33:
        s = 2.0 * sqrt(1.0 + m.a11 - m.a22 - m.a33)
        q.x = 0.25 * s
        s = 1.0 / s
        q.w = -s * (m.a23 - m.a32)
        q.y = s * (m.a21 + m.a12)
        q.z = s * (m.a31 + m.a13)
    elif m.a22 > m.a33:
        s = 2.0 * sqrt(1.0 + m.a22 - m.a11 - m.a33)
        q.y = 0.25 * s
        s = 1.0 / s
        q.w = -s * (m.a31 - m.a13)
        q.x = s * (m.a21 + m.a12)
        q.z = s * (m.a32 + m.a23)
    else:
        s = 2.0 * sqrt(1.0 + m.a33 - m.a11 - m.a22)
        q.z = 0.25 * s
        s = 1.0 / s
        q.w = -s * (m.a12 - m.a21)
        q.x = s * (m.a31 + m.a13)
        q.y = s * (m.a32 + m.a23)
