import cython
from libc.math cimport M_PI as PI, sqrt, abs, sin, cos, asin, acos, atan2, copysign
from ... math cimport quaternionNormalize_InPlace, normalizeVec3_InPlace
from ... algorithms.random_number_generators cimport XoShiRo256Plus

from ... data_structures cimport (
    Vector3DList, EulerList, DoubleList, Matrix4x4List,
    VirtualDoubleList, Quaternion, QuaternionList
)

cdef float degreeToRadianFactor = <float>(PI / 180)
cdef float radianToDegreeFactor = <float>(180 / PI)

def combineEulerList(Py_ssize_t amount,
                     VirtualDoubleList x, VirtualDoubleList y, VirtualDoubleList z,
                     bint useDegree = False):
    cdef EulerList output = EulerList(length = amount)
    cdef float factor = degreeToRadianFactor if useDegree else 1
    cdef Py_ssize_t i
    for i in range(amount):
        output.data[i].x = <float>x.get(i) * factor
        output.data[i].y = <float>y.get(i) * factor
        output.data[i].z = <float>z.get(i) * factor
        output.data[i].order = 0
    return output

def vectorsToEulers(Vector3DList vectors, bint useDegree):
    cdef EulerList eulers = EulerList(length = len(vectors))
    cdef Py_ssize_t i
    if useDegree:
        for i in range(len(vectors)):
            eulers.data[i].order = 0
            eulers.data[i].x = vectors.data[i].x * degreeToRadianFactor
            eulers.data[i].y = vectors.data[i].y * degreeToRadianFactor
            eulers.data[i].z = vectors.data[i].z * degreeToRadianFactor
    else:
        for i in range(len(vectors)):
            eulers.data[i].order = 0
            eulers.data[i].x = vectors.data[i].x
            eulers.data[i].y = vectors.data[i].y
            eulers.data[i].z = vectors.data[i].z
    return eulers

def eulersToVectors(EulerList eulers, bint useDegree):
    cdef Vector3DList vectors = Vector3DList(length = len(eulers))
    cdef Py_ssize_t i
    if useDegree:
        for i in range(len(eulers)):
            vectors.data[i].x = eulers.data[i].x * radianToDegreeFactor
            vectors.data[i].y = eulers.data[i].y * radianToDegreeFactor
            vectors.data[i].z = eulers.data[i].z * radianToDegreeFactor
    else:
        for i in range(len(eulers)):
            vectors.data[i].x = eulers.data[i].x
            vectors.data[i].y = eulers.data[i].y
            vectors.data[i].z = eulers.data[i].z
    return vectors

def getAxisListOfEulerList(EulerList eulers, str axis, bint useDegree):
    assert axis in "xyz"
    cdef DoubleList output = DoubleList(length = eulers.length)
    cdef float factor = radianToDegreeFactor if useDegree else 1
    cdef Py_ssize_t i
    if axis == "x":
        for i in range(output.length):
            output.data[i] = eulers.data[i].x * factor
    elif axis == "y":
        for i in range(output.length):
            output.data[i] = eulers.data[i].y * factor
    elif axis == "z":
        for i in range(output.length):
            output.data[i] = eulers.data[i].z * factor
    return output

def combineQuaternionList(Py_ssize_t amount,
                          VirtualDoubleList w, VirtualDoubleList x,
                          VirtualDoubleList y, VirtualDoubleList z):
    cdef QuaternionList output = QuaternionList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        output.data[i].w = <float>w.get(i)
        output.data[i].x = <float>x.get(i)
        output.data[i].y = <float>y.get(i)
        output.data[i].z = <float>z.get(i)
        quaternionNormalize_InPlace(&output.data[i])
    return output

def getAxisListOfQuaternionList(QuaternionList quaternions, str axis):
    assert axis in "wxyz"
    cdef DoubleList output = DoubleList(length = quaternions.length)
    cdef Py_ssize_t i
    if axis == "w":
        for i in range(output.length):
            output.data[i] = quaternions.data[i].w
    elif axis == "x":
        for i in range(output.length):
            output.data[i] = quaternions.data[i].x
    elif axis == "y":
        for i in range(output.length):
            output.data[i] = quaternions.data[i].y
    elif axis == "z":
        for i in range(output.length):
            output.data[i] = quaternions.data[i].z
    return output

#base on the expression from http://planning.cs.uiuc.edu/node198.html
def randomQuaternionList(int seed, int amount):
    cdef QuaternionList result = QuaternionList(length = amount)
    cdef XoShiRo256Plus rng = XoShiRo256Plus(seed)
    cdef double u1, u2, u3, k1, k2
    cdef Py_ssize_t i
    for i in range(amount):
        u1 = rng.nextFloat()
        u2 = rng.nextFloat() * 2 * PI
        u3 = rng.nextFloat() * 2 * PI
        k1 = sqrt(1 - u1)
        k2 = sqrt(u1)
        result.data[i].w = k1 * sin(u2)
        result.data[i].x = k1 * cos(u2)
        result.data[i].y = k2 * sin(u3)
        result.data[i].z = k2 * cos(u3)
        quaternionNormalize_InPlace(result.data + i)

    return result

def quaternionsToMatrices(QuaternionList q):
    cdef Py_ssize_t count = len(q)
    cdef Matrix4x4List m = Matrix4x4List(length = count)
    cdef double sqw, sqx, sqy, sqz, invs, tmp1, tmp2

    for i in range(count):
        sqw = q.data[i].w * q.data[i].w
        sqx = q.data[i].x * q.data[i].x
        sqy = q.data[i].y * q.data[i].y
        sqz = q.data[i].z * q.data[i].z
        invs = 1 / (sqx + sqy + sqz + sqw)

        m.data[i].a11 = ( sqx - sqy - sqz + sqw)*invs
        m.data[i].a22 = (-sqx + sqy - sqz + sqw)*invs
        m.data[i].a33 = (-sqx - sqy + sqz + sqw)*invs

        tmp1 = q.data[i].x * q.data[i].y
        tmp2 = q.data[i].z * q.data[i].w
        m.data[i].a21 = 2.0 * (tmp1 + tmp2)*invs
        m.data[i].a12 = 2.0 * (tmp1 - tmp2)*invs

        tmp1 = q.data[i].x * q.data[i].z
        tmp2 = q.data[i].y * q.data[i].w
        m.data[i].a31 = 2.0 * (tmp1 - tmp2)*invs
        m.data[i].a13 = 2.0 * (tmp1 + tmp2)*invs

        tmp1 = q.data[i].y * q.data[i].z
        tmp2 = q.data[i].x * q.data[i].w
        m.data[i].a32 = 2.0 * (tmp1 + tmp2)*invs
        m.data[i].a23 = 2.0 * (tmp1 - tmp2)*invs

        m.data[i].a14 = m.data[i].a24 = m.data[i].a34 = 0
        m.data[i].a41 = m.data[i].a42 = m.data[i].a43 = 0
        m.data[i].a44 = 1

    return m

#base on https://en.m.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
#base on https://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions
def eulersToQuaternions(EulerList eulers):
    cdef Py_ssize_t i
    cdef int count = eulers.getLength()
    cdef QuaternionList q = QuaternionList(length=count)
    cdef double cr, sr, cp, sp, cy, sy

    for i in range(count):
        cr = cos(eulers.data[i].x * 0.5)
        sr = sin(eulers.data[i].x * 0.5)
        cp = cos(eulers.data[i].y * 0.5)
        sp = sin(eulers.data[i].y * 0.5)
        cy = cos(eulers.data[i].z * 0.5)
        sy = sin(eulers.data[i].z * 0.5)

        q.data[i].w = cr * cp * cy + sr * sp * sy
        q.data[i].x = sr * cp * cy - cr * sp * sy
        q.data[i].y = cr * sp * cy + sr * cp * sy
        q.data[i].z = cr * cp * sy - sr * sp * cy
        quaternionNormalize_InPlace(q.data + i)

    return q

@cython.cdivision(True)
def quaternionsToEulers(QuaternionList q):
    cdef Py_ssize_t i
    cdef int count = q.getLength()
    cdef EulerList eulers = EulerList(length=count)
    cdef double sinr_cosp, cosr_cosp, sinp, siny_cosp, cosy_cosp, sqw, sqx, sqy, sqz, invs

    for i in range(count):
        sqw = q.data[i].w * q.data[i].w
        sqx = q.data[i].x * q.data[i].x
        sqy = q.data[i].y * q.data[i].y
        sqz = q.data[i].z * q.data[i].z
        invs = 1 / sqrt(sqx + sqy + sqz + sqw)

        sinr_cosp = 2 * (q.data[i].w * q.data[i].x + q.data[i].y * q.data[i].z) * invs
        cosr_cosp = 1 - 2 * (q.data[i].x * q.data[i].x + q.data[i].y * q.data[i].y) * invs
        sinp = 2 * (q.data[i].w * q.data[i].y - q.data[i].z * q.data[i].x) * invs
        siny_cosp = 2 * (q.data[i].w * q.data[i].z + q.data[i].x * q.data[i].y) * invs
        cosy_cosp = 1 - 2 * (q.data[i].y * q.data[i].y + q.data[i].z * q.data[i].z) * invs

        eulers.data[i].x = atan2(sinr_cosp, cosr_cosp)
        if abs(sinp) >= 1:
            eulers.data[i].y = copysign(PI / 2, sinp)
        else:
            eulers.data[i].y = asin(sinp)
        eulers.data[i].z = atan2(siny_cosp, cosy_cosp)
        eulers.data[i].order = 0

    return eulers

def axises_AnglesToQuaternions(Vector3DList a, DoubleList angles, bint usedegree=False):
    cdef Py_ssize_t i
    cdef int count = len(a)
    cdef double u1, u2
    cdef QuaternionList q = QuaternionList(length=count)

    for i in range(count):
        u1 = sin(angles.data[i]/2)
        u2 = cos(angles.data[i]/2)
        if usedegree == False:
            angles.data[i] = angles.data[i]
        else:
            angles.data[i] = angles.data[i] * degreeToRadianFactor

        normalizeVec3_InPlace(a.data + i)
        q.data[i].x = a.data[i].x * u1
        q.data[i].y = a.data[i].y * u1
        q.data[i].z = a.data[i].z * u1
        q.data[i].w = u2
        quaternionNormalize_InPlace(q.data + i)

    return q

def quaternionsToAxises_Angles(QuaternionList q, bint usedegree=False):
    cdef Py_ssize_t i
    cdef int count = len(q)
    cdef double k, u
    cdef Vector3DList a = Vector3DList(length=count)
    cdef DoubleList angles = DoubleList(length=count)

    for i in range(count):
        quaternionNormalize_InPlace(q.data + i)
        k = sqrt(1 - q.data[i].w * q.data[i].w)
        u = 2 * acos(q.data[i].w)
        if usedegree == False:
            angles.data[i] = u
        else:
            angles.data[i] = u * radianToDegreeFactor
        a.data[i].x = q.data[i].x / k
        a.data[i].y = q.data[i].y / k
        a.data[i].z = q.data[i].z / k
        normalizeVec3_InPlace(a.data + i)

    return a, angles
