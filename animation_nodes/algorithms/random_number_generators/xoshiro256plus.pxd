from libc.stdint cimport uint64_t

cdef class XoShiRo256Plus:
    cdef uint64_t s0
    cdef uint64_t s1
    cdef uint64_t s2
    cdef uint64_t s3

    cdef uint64_t nextUInt64(self)
    cdef double nextDouble(self)
    cdef double nextDoubleInRange(self, double start, double end)
    cdef float nextFloat(self)
    cdef float nextFloatInRange(self, float start, float end)
