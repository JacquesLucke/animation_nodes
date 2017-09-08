# distutils: language = c++
# TODO: make path cross platform
# distutils: sources = source\FastNoiseSIMD.cpp source\FastNoiseSIMD_sse2.cpp source\FastNoiseSIMD_sse41.cpp source\FastNoiseSIMD_internal.cpp

cdef extern from "source\\FastNoiseSIMD.h":
    cdef cppclass FastNoiseSIMD:
        @staticmethod
        FastNoiseSIMD* NewFastNoiseSIMD(int seed)
        @staticmethod
        int GetSIMDLevel()

        float* GetSimplexFractalSet(int xStart, int yStart, int zStart, int xSize, int zSize, int zSize)


cdef FastNoiseSIMD *f =  FastNoiseSIMD.NewFastNoiseSIMD(1234)
print(f.GetSIMDLevel())

cdef float *noise = f.GetSimplexFractalSet(0, 0, 0, 256, 256, 1)
from ... data_structures cimport Vector3DList
cdef Py_ssize_t i, x, y
cdef Vector3DList vectors = Vector3DList(length = 256 * 256)

vecs = vectors

for x in range(256):
    for y in range(256):
        vectors.data[i].x = x
        vectors.data[i].y = y
        vectors.data[i].z = noise[i]
        i += 1
