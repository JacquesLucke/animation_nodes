from libc.limits cimport INT_MAX
from ... math cimport Euler3
from .. random cimport uniformRandomNumber
from ... data_structures cimport EulerList, Vector3DList

def generateRandomVectors(seed, count, double scale):
    cdef:
        int length = min(max(count, 0), INT_MAX)
        int startSeed = (seed * 763645) % INT_MAX
        Vector3DList newList = Vector3DList(length = length)
        float* _data = <float*>newList.data
        int i

    for i in range(length * 3):
        _data[i] = uniformRandomNumber(startSeed + i, -scale, scale)

    return newList

def generateRandomEulers(seed, count, double scale):
    cdef:
        int length = min(max(count, 0), INT_MAX)
        int startSeed = (seed * 876521) % INT_MAX
        EulerList newList = EulerList(length = length)
        Euler3* _data = <Euler3*>newList.data
        int i, seedOffset

    for i in range(length):
        seedOffset = i * 3
        _data[i].x = uniformRandomNumber(startSeed + seedOffset + 0, -scale, scale)
        _data[i].y = uniformRandomNumber(startSeed + seedOffset + 1, -scale, scale)
        _data[i].z = uniformRandomNumber(startSeed + seedOffset + 2, -scale, scale)
        _data[i].order = 0

    return newList
