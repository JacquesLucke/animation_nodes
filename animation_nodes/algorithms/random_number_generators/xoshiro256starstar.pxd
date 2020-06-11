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
    cdef uint64_t nextUInt64UpperBound(self, uint64_t n)
    cdef long long nextLongLongUpperBound(self, uint64_t n)
    cdef long nextLongUpperBound(self, uint64_t n)
    cdef int nextIntUpperBound(self, uint64_t n)
    cdef uint64_t nextUInt64DoubleBound(self, uint64_t start, uint64_t end)
    cdef long long nextLongLongDoubleBound(self, uint64_t start, uint64_t end)
    cdef long nextLongDoubleBound(self, uint64_t start, uint64_t end)
    cdef int nextIntDoubleBound(self, uint64_t start, uint64_t end)
