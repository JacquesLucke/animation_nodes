from libc.stdint cimport uint64_t

cdef class XoShiRo256StarStar:
    cdef uint64_t s0
    cdef uint64_t s1
    cdef uint64_t s2
    cdef uint64_t s3

    cdef uint64_t nextUInt64(self)
    cdef long long nextLongLong(self)
    cdef long nextLong(self)
    cdef int nextInt(self)
    cdef bint nextBoolean(self)

    cdef uint64_t nextUInt64WithMax(self, uint64_t maximum)
    cdef long long nextLongLongWithMax(self, uint64_t maximum)
    cdef long nextLongWithMax(self, uint64_t maximum)
    cdef int nextIntWithMax(self, uint64_t maximum)

    cdef uint64_t nextUInt64InRange(self, uint64_t start, uint64_t end)
    cdef long long nextLongLongInRange(self, uint64_t start, uint64_t end)
    cdef long nextLongInRange(self, uint64_t start, uint64_t end)
    cdef int nextIntInRange(self, uint64_t start, uint64_t end)
