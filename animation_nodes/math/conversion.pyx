from mathutils import Vector, Matrix, Euler
from mathutils import Quaternion as PyQuaternion
from .. data_structures.color import Color as PyColor
from libc.math cimport M_PI as PI, sqrt, abs, sin, cos, asin, acos, atan2, copysign

# Vectors
##########################################################

cdef Vector2 toVector2(value) except *:
    cdef Vector2 v
    setVector2(&v, value)
    return v

cdef setVector2(Vector2* v, value):
    if len(value) != 2:
        raise TypeError("element is not a 2D vector")
    v.x = value[0]
    v.y = value[1]

cdef toPyVector2(Vector2* v):
    return Vector((v.x, v.y))


cdef Vector3 toVector3(value) except *:
    cdef Vector3 v
    setVector3(&v, value)
    return v

cdef setVector3(Vector3* v, value):
    if len(value) != 3:
        raise TypeError("element is not a 3D vector")
    v.x = value[0]
    v.y = value[1]
    v.z = value[2]

cdef toPyVector3(Vector3* v):
    return Vector((v.x, v.y, v.z))


cdef Vector4 toVector4(value) except *:
    cdef Vector4 v
    setVector4(&v, value)
    return v

cdef setVector4(Vector4* v, value):
    if len(value) != 4:
        raise TypeError("element is not a 3D vector")
    v.x = value[0]
    v.y = value[1]
    v.z = value[2]
    v.w = value[3]

cdef toPyVector4(Vector4* v):
    return Vector((v.x, v.y, v.z, v.w))


# Matrices
##########################################################

cdef Matrix4 toMatrix4(value) except *:
    cdef Matrix4 m
    setMatrix4(&m, value)
    return m

cdef setMatrix4(Matrix4* m, value):
    if not (len(value.row) == len(value.col) == 4):
        raise TypeError("element is not a 4x4 matrix")

    row1 = value[0]
    row2 = value[1]
    row3 = value[2]
    row4 = value[3]
    m.a11, m.a12, m.a13, m.a14 = row1[0], row1[1], row1[2], row1[3]
    m.a21, m.a22, m.a23, m.a24 = row2[0], row2[1], row2[2], row2[3]
    m.a31, m.a32, m.a33, m.a34 = row3[0], row3[1], row3[2], row3[3]
    m.a41, m.a42, m.a43, m.a44 = row4[0], row4[1], row4[2], row4[3]


cdef toPyMatrix4(Matrix4* m):
    return Matrix(((m.a11, m.a12, m.a13, m.a14),
                   (m.a21, m.a22, m.a23, m.a24),
                   (m.a31, m.a32, m.a33, m.a34),
                   (m.a41, m.a42, m.a43, m.a44)))

cdef toPyMatrix3(Matrix3* m):
    return Matrix(((m.a11, m.a12, m.a13),
                   (m.a21, m.a22, m.a23),
                   (m.a31, m.a32, m.a33)))


# Eulers
##########################################################

cdef Euler3 toEuler3(value) except *:
    cdef Euler3 e
    setEuler3(&e, value)
    return e

cdef setEuler3(Euler3* e, value):
    if len(value) != 3:
        raise TypeError("value is no euler value")
    e.x = value[0]
    e.y = value[1]
    e.z = value[2]
    cdef str order
    if isinstance(value, Euler):
        order = value.order
        if   order == "XYZ": e.order = 0
        elif order == "XZY": e.order = 1
        elif order == "YXZ": e.order = 2
        elif order == "YZX": e.order = 3
        elif order == "ZXY": e.order = 4
        elif order == "ZYX": e.order = 5
    else:
        e.order = 0

cdef toPyEuler3(Euler3* e):
    if e.order == 0: return Euler((e.x, e.y, e.z), "XYZ")
    if e.order == 1: return Euler((e.x, e.y, e.z), "XZY")
    if e.order == 2: return Euler((e.x, e.y, e.z), "YXZ")
    if e.order == 3: return Euler((e.x, e.y, e.z), "YZX")
    if e.order == 4: return Euler((e.x, e.y, e.z), "ZXY")
    if e.order == 5: return Euler((e.x, e.y, e.z), "ZYX")
    
cdef eulerToQuaternionInPlace(Quaternion* q, Euler3 *e):
    cdef float cr = cos(e.x * 0.5)
    cdef float sr = sin(e.x * 0.5)
    cdef float cp = cos(e.y * 0.5)
    cdef float sp = sin(e.y * 0.5)
    cdef float cy = cos(e.z * 0.5)
    cdef float sy = sin(e.z * 0.5)
    
    q.w = cr * cp * cy + sr * sp * sy
    q.x = sr * cp * cy - cr * sp * sy
    q.y = cr * sp * cy + sr * cp * sy
    q.z = cr * cp * sy - sr * sp * cy

# Quaternions
##########################################################

cdef Quaternion toQuaternion(value) except *:
    cdef Quaternion q
    setQuaternion(&q, value)
    return q

cdef setQuaternion(Quaternion* q, value):
    q.w = value.w
    q.x = value.x
    q.y = value.y
    q.z = value.z

cdef toPyQuaternion(Quaternion* q):
    return PyQuaternion((q.w, q.x, q.y, q.z))

cdef quaternionToMatrix4Inplace(Matrix4 *m, Quaternion *q):
    cdef float sqw = q.w * q.w
    cdef float sqx = q.x * q.x
    cdef float sqy = q.y * q.y
    cdef float sqz = q.z * q.z

    cdef invs = 1 / (sqx + sqy + sqz +sqw)

    m.a11 = (sqx - sqy - sqz + sqw) * invs
    m.a22 = (-sqx + sqy - sqz + sqw) * invs
    m.a33 = (-sqx - sqy + sqz + sqw) * invs

    cdef tmp1 = q.x * q.y
    cdef tmp2 = q.z * q.w

    m.a21 = 2.0 * (tmp1 + tmp2) * invs
    m.a12 = 2.0 * (tmp1 - tmp2) * invs

    tmp1 = q.x * q.z
    tmp2 = q.y * q.w

    m.a31 = 2.0 * (tmp1 - tmp2) * invs
    m.a13 = 2.0 * (tmp1 + tmp2) * invs

    tmp1 = q.y * q.z
    tmp2 = q.x * q.w

    m.a32 = 2.0 * (tmp1 + tmp2) * invs
    m.a23 = 2.0 * (tmp1 - tmp2) * invs

#base on https://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions
cdef quaternionToEulerInPlace(Euler3 *e, Quaternion *q):
    cdef float sinr_cosp = 2 * (q.w * q.x + q.y * q.z)
    cdef float cosr_cosp = 1 - 2 * (q.x * q.x + q.y * q.y)
    e.x = atan2(sinr_cosp, cosr_cosp)

    cdef float sinp = 2 * (q.w * q.y - q.z * q.x)
    if abs(sinp) >= 1.0:
        e.y = copysign(M_PI/2, sinp)
    else:
        e.y = asin(sinp)

    cdef float siny_cosp = 2 * (q.w * q.z + q.x * q.y)
    cdef float cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
    e.z = atan2(siny_cosp, cosy_cosp)
    e.order = 0

#base on https://en.m.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
cdef quaternionToAxis_AngleInPlace(Vector3 *v, float a, Quaternion *q):
    quaternionNormalize_InPlace(q)
    cdef float k = sqrt(1 - q.w * q.w)
    cdef float u = 2 * acos(q.w)
    
    v.x = q.x / k
    v.y = q.y / k
    v.z = q.z / k
    a = u
    
cdef axis_AngleToQuaternionInPlace(Quaternion *q, Vector3 *v, float a):
    #normalizeVec3_InPlace(v)
    cdef u1 = sin(a / 2)
    cdef u2 = cos(a / 2)
    
    q.w = u2
    q.x = v.x * u1
    q.y = v.y * u1
    q.z = v.z * u1
    
# Colors
###########################################################

cdef Color toColor(value) except *:
    cdef Color c
    setColor(&c, value)
    return c

cdef setColor(Color* c, value):
    if len(value) != 4:
        raise TypeError("Element is not a color.")
    c.r = value[0]
    c.g = value[1]
    c.b = value[2]
    c.a = value[3]

cdef toPyColor(Color* c):
    return PyColor((c.r, c.g, c.b, c.a))
