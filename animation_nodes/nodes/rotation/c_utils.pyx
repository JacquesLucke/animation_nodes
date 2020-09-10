from libc.math cimport M_PI as PI, sqrt, sin, cos
from ... math cimport quaternionNormalize_InPlace
from ... algorithms.random_number_generators cimport XoShiRo256Plus

from ... data_structures cimport (
    Vector3DList, EulerList, DoubleList,
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
