from ... data_structures cimport Vector3DList, EulerList, DoubleList
from libc.math cimport M_PI as PI
cdef float degreeToRadianFactor = <float>(PI / 180)
cdef float radianToDegreeFactor = <float>(180 / PI)

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
