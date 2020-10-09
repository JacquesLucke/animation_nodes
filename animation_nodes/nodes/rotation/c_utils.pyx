from libc.math cimport M_PI as PI, sqrt, sin, cos, asin, acos
from ... math cimport (
    quaternionNormalize_InPlace, normalizeVec3_InPlace,
    eulerToQuaternionInPlace, quaternionToMatrix4Inplace,
    quaternionToEulerInPlace, quaternionToAxis_AngleInPlace,
    axis_AngleToQuaternionInPlace
)
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

    for i in range(count):
        quaternionToMatrix4Inplace(&m.data[i], &q.data[i])
    return m

#base on https://en.m.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
#base on https://www.euclideanspace.com/maths/algebra/realNormedAlgebra/quaternions
def eulersToQuaternions(EulerList e):
    cdef Py_ssize_t i
    cdef int count = e.getLength()
    cdef QuaternionList q = QuaternionList(length=count)

    for i in range(count):
        eulerToQuaternionInPlace(&q.data[i], &e.data[i])
        quaternionNormalize_InPlace(q.data + i)

    return q

def quaternionsToEulers(QuaternionList q):
    cdef Py_ssize_t i
    cdef int count = q.getLength()
    cdef EulerList e = EulerList(length=count)
    e.fill(0)

    for i in range(count):
        quaternionToEulerInPlace(&e.data[i], &q.data[i])

    return e

def axises_AnglesToQuaternions(Vector3DList a, DoubleList angles, bint usedegree=False):
    cdef Py_ssize_t i
    cdef int count = len(a)
    cdef QuaternionList q = QuaternionList(length=count)

    for i in range(count):
        if usedegree == False:
            angles.data[i] = angles.data[i]
        else:
            angles.data[i] = angles.data[i] * degreeToRadianFactor

        axis_AngleToQuaternionInPlace(&q.data[i], &a.data[i], angles.data[i])
        quaternionNormalize_InPlace(q.data + i)

    return q

def quaternionsToAxises_Angles(QuaternionList q, bint usedegree=False):
    cdef Py_ssize_t i
    cdef int count = len(q)
    cdef double u
    cdef Vector3DList a = Vector3DList(length=count)
    cdef DoubleList angles = DoubleList(length=count)

    for i in range(count):
        u = 2 * acos(q.data[i].w)
        if usedegree == False:
            angles.data[i] = u
        else:
            angles.data[i] = u * radianToDegreeFactor
        quaternionToAxis_AngleInPlace(&a.data[i], angles.data[i], &q.data[i])
        normalizeVec3_InPlace(a.data + i)

    return a, angles
