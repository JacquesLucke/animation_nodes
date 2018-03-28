from libc.math cimport M_PI as PI
from libc.math cimport sqrt

from ... math cimport Euler3
from ... utils.limits cimport INT_MAX
from ... data_structures cimport EulerList, Vector3DList
from .. random cimport randomFloat_Range, randomVector3_Normalized, randomFloat_ScaledRange

def generateRandomVectors(seed, count, float scale, bint normalized = False):
    cdef:
        int length = min(max(count, 0), INT_MAX)
        int startSeed = (seed * 763645) % INT_MAX
        Vector3DList newList = Vector3DList(length = length)

    if normalized:
        insertRandomVectors_Normalized(startSeed, newList, scale)
    else:
        insertRandomVectors_Simple(startSeed, newList, scale)
    return newList

cdef insertRandomVectors_Simple(int startSeed, Vector3DList vectors, float scale):
    cdef Py_ssize_t i
    cdef float *_data = <float*>vectors.data
    for i in range(len(vectors) * 3):
        _data[i] = randomFloat_ScaledRange(startSeed + i, scale)

cdef insertRandomVectors_Normalized(int startSeed, Vector3DList vectors, float scale):
    cdef Py_ssize_t i
    for i in range(len(vectors)):
        randomVector3_Normalized(startSeed + i, <float*>(vectors.data + i), scale)

def generateRandomEulers(seed, count, double scale):
    cdef:
        int length = min(max(count, 0), INT_MAX)
        int startSeed = (seed * 876521) % INT_MAX
        EulerList newList = EulerList(length = length)
        Euler3 *_data = <Euler3*>newList.data
        int i, seedOffset

    for i in range(length):
        seedOffset = i * 3
        _data[i].x = randomFloat_ScaledRange(startSeed + seedOffset + 0, scale)
        _data[i].y = randomFloat_ScaledRange(startSeed + seedOffset + 1, scale)
        _data[i].z = randomFloat_ScaledRange(startSeed + seedOffset + 2, scale)
        _data[i].order = 0

    return newList
