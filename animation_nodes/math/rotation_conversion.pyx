cimport cython
from . vector cimport lengthVec3
from . conversion cimport toPyEuler3
from . matrix cimport setIdentityMatrix
from . quaternion cimport setUnitQuaternion
from mathutils import Vector, Matrix, Euler
from . matrix cimport normalizeMatrix_3x3_Part
from libc.math cimport (
    M_PI as PI, sqrt, hypot, abs,
    sin, cos, asin, acos, atan2, copysign
)

# Matrix to Euler
################################################################

def matrix4x4ListToEulerList(Matrix4x4List matrices, bint isNormalized = False):
    cdef EulerList rotations = EulerList(length = matrices.length)
    cdef long i
    if isNormalized:
        for i in range(rotations.length):
            normalizedMatrixToEuler(rotations.data + i, matrices.data + i)
    else:
        for i in range(rotations.length):
            matrixToEuler(rotations.data + i, matrices.data + i)
    return rotations

cdef matrixToEuler(Euler3* target, Matrix3_or_Matrix4* m):
    cdef Matrix3_or_Matrix4 _m
    normalizeMatrix_3x3_Part(&_m, m)
    normalizedMatrixToEuler(target, &_m)

cdef normalizedMatrixToEuler(Euler3* e, Matrix3_or_Matrix4* m):
    cdef Euler3 e1, e2
    normalizedMatrixToEuler2(&e1, &e2, m)

    cdef float abs1 = abs(e1.x) + abs(e1.y) + abs(e1.z)
    cdef float abs2 = abs(e2.x) + abs(e2.y) + abs(e2.z)

    if abs1 < abs2:
        e[0] = e1
    else:
        e[0] = e2

cdef normalizedMatrixToEuler2(Euler3* e1, Euler3* e2, Matrix3_or_Matrix4* m):
    '''Create 2 eulers and pick the better one later'''
    cdef float cy = hypot(m.a11, m.a21)
    e1.order = e2.order = 0
    if cy > 0.000001:
        e1.x = atan2(m.a32, m.a33)
        e1.y = atan2(-m.a31, cy)
        e1.z = atan2(m.a21, m.a11)

        e2.x = atan2(-m.a32, -m.a33)
        e2.y = atan2(-m.a31, -cy)
        e2.z = atan2(-m.a21, -m.a11)
    else:
        e1.x = e2.x = atan2(-m.a23, m.a22)
        e1.y = e2.y = atan2(-m.a31, cy)
        e1.z = e2.z = 0.0

# Matrix to Quaternion
################################################################

def matrix4x4ListToQuaternionList(Matrix4x4List matrices, bint isNormalized = False):
    cdef QuaternionList quaternions = QuaternionList(length = matrices.length)
    cdef long i
    if isNormalized:
        for i in range(quaternions.length):
            normalizedMatrixToQuaternion(quaternions.data + i, matrices.data + i)
    else:
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

# Axis Angle to Matrix
###########################################

cdef void normalizedAxisAngleToMatrix(Matrix3_or_Matrix4* m, Vector3* axis, float angle):
    normalizedAxisCosAngleToMatrix(m, axis, cos(angle))

cdef void normalizedAxisCosAngleToMatrix(Matrix3_or_Matrix4* m, Vector3* axis, float cosAngle):
    cdef float c = cosAngle
    cdef float s = sqrt(1.0 - c * c)
    cdef float t = 1 - c
    cdef float x, y, z
    x, y, z = axis.x, axis.y, axis.z

    m.a11, m.a12, m.a13 = t*x*x+c,    t*x*y-z*s,  t*x*z+y*s
    m.a21, m.a22, m.a23 = t*x*y+z*s,  t*y*y+c,    t*y*z-x*s
    m.a31, m.a32, m.a33 = t*x*z-y*s,  t*y*z+x*s,  t*z*z+c

    if Matrix3_or_Matrix4 is Matrix4:
        m.a14, m.a24, m.a34 = 0, 0, 0
        m.a41, m.a42, m.a43, m.a44 = 0, 0, 0, 1

# Euler to Quaternion
##########################################################    
        
# https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
cdef void euler3ToQuaternion(Quaternion *q, Euler3 *e):
    cdef float cx = cos(e.x * 0.5)
    cdef float sx = sin(e.x * 0.5)
    cdef float cy = cos(e.y * 0.5)
    cdef float sy = sin(e.y * 0.5)
    cdef float cz = cos(e.z * 0.5)
    cdef float sz = sin(e.z * 0.5)
    
    cdef float cxcy = cx * cy
    cdef float sxcy = sx * cy
    cdef float sxsy = sx * sy
    cdef float cxsy = cx * sy
    
    q.w = cxcy * cz + sxsy * sz
    q.x = sxcy * cz - cxsy * sz
    q.y = cxsy * cz + sxcy * sz
    q.z = cxcy * sz - sxsy * cz
    
# Quaternion to Euler
##########################################################

# https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
cdef void quaternionToEuler3(Euler3 *e, Quaternion *q):
    cdef float sinrCosp = 2 * (q.w * q.x + q.y * q.z)
    cdef float cosrCosp = 1 - 2 * (q.x * q.x + q.y * q.y)
    e.x = atan2(sinrCosp, cosrCosp)

    cdef float sinp = 2 * (q.w * q.y - q.z * q.x)
    if abs(sinp) >= 1.0:
        e.y = copysign(PI / 2, sinp)
    else:
        e.y = asin(sinp)

    cdef float sinyCosp = 2 * (q.w * q.z + q.x * q.y)
    cdef float cosyCosp = 1 - 2 * (q.y * q.y + q.z * q.z)
    e.z = atan2(sinyCosp, cosyCosp)
    e.order = 0

# Quaternion to Matrix
##########################################################

# https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToMatrix/index.htm

@cython.cdivision(True)
cdef void quaternionToMatrix4(Matrix4 *m, Quaternion *q):
    cdef float w, x, y, z
    w, x, y, z = q.w, q.x, q.y, q.z
    cdef float ww = w * w
    cdef float xx = x * x
    cdef float yy = y * y
    cdef float zz = z * z

    cdef float xy = x * y
    cdef float xz = x * z
    cdef float yz = y * z
    cdef float zw = z * w
    cdef float yw = y * w
    cdef float xw = x * w

    cdef float dot = xx + yy + zz + ww
    if dot == 0:
        setIdentityMatrix(m)
        return

    cdef float invs = 1 / dot

    m.a11 = (xx - yy - zz + ww) * invs
    m.a22 = (-xx + yy - zz + ww) * invs
    m.a33 = (-xx - yy + zz + ww) * invs

    m.a21 = 2.0 * (xy + zw) * invs
    m.a12 = 2.0 * (xy - zw) * invs

    m.a31 = 2.0 * (xz - yw) * invs
    m.a13 = 2.0 * (xz + yw) * invs

    m.a32 = 2.0 * (yz + xw) * invs
    m.a23 = 2.0 * (yz - xw) * invs
    
    m.a44 = 1.0
    m.a14 = m.a24 = m.a34 = 0.0
    m.a41 = m.a42 = m.a43 = 0.0

# Quaternion from AxisAngle
##########################################################

@cython.cdivision(True)
cdef void quaternionFromAxisAngle(Quaternion *q, Vector3 *axis, float angle):
    cdef float axisLength = lengthVec3(axis)
    if axisLength < 0.000001:
        setUnitQuaternion(q)
        return

    cdef float ca = cos(angle)

    # in case the float library is not accurate
    if ca > 1: ca = 1
    elif ca < -1: ca = -1

    cdef float cq = sqrt((1 + ca) / 2) # cos(acos(ca) / 2)
    cdef float sq = sqrt((1 - ca) / 2) # sin(acos(ca) / 2)

    cdef float factor = sq / axisLength
    q.x = axis.x * factor
    q.y = axis.y * factor
    q.z = axis.z * factor
    q.w = cq

# Quaternion to AxisAngle
##########################################################

# https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToAngle/index.htm
@cython.cdivision(True)
cdef void quaternionToAxisAngle(Vector3 *v, float *a, Quaternion *q):
    cdef float k = sqrt(1 - q.w * q.w)

    if k == 0:
        v.x = 1
        v.y = 0
        v.z = 0 
    else:
        v.x = q.x / k
        v.y = q.y / k
        v.z = q.z / k
    
    a[0] = <float>(2 * acos(q.w))
