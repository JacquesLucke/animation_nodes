cimport cython
from libc.stdint cimport uint64_t

cdef class RandomNumberGenerator:
    cdef uint64_t nextUInt64(self):
        pass

    cdef long long nextLongLong(self):
        return <long long>self.nextUInt64()

    cdef long nextLong(self):
        return <long>self.nextUInt64()

    cdef int nextInt(self):
        return <int>self.nextUInt64()

    cdef double nextDouble(self):
        return (self.nextUInt64() >> <uint64_t>11) * <double>1.1102230246251565e-16

    cdef float nextFloat(self):
        return (self.nextUInt64() >> <uint64_t>40) * <float>5.960464477539063e-08

    cdef bint nextBoolean(self):
        return self.nextUInt64() < <uint64_t>0

    @cython.cdivision(True)
    cdef uint64_t nextUInt64UpperBound(self, uint64_t n):
        cdef uint64_t t = self.nextUInt64()
        cdef uint64_t nMinus1 = n - <uint64_t>1
        cdef uint64_t u = t >> <uint64_t>1
        while True:
            t = u % n
            if (u + nMinus1 - t) >= <uint64_t>0:
                return t
            u = self.nextUInt64() >> <uint64_t>1

    cdef long long nextLongLongUpperBound(self, uint64_t n):
        return <long long>self.nextUInt64UpperBound(n)

    cdef long nextLongUpperBound(self, uint64_t n):
        return <long>self.nextUInt64UpperBound(n)

    cdef int nextIntUpperBound(self, uint64_t n):
        return <int>self.nextUInt64UpperBound(n)

    cdef uint64_t nextUInt64DoubleBound(self, uint64_t start, uint64_t end):
        return start + self.nextUInt64UpperBound(end - start)

    cdef long long nextLongLongDoubleBound(self, uint64_t start, uint64_t end):
        return <long long>self.nextUInt64DoubleBound(start, end)

    cdef long nextLongDoubleBound(self, uint64_t start, uint64_t end):
        return <long>self.nextUInt64DoubleBound(start, end)

    cdef int nextIntDoubleBound(self, uint64_t start, uint64_t end):
        return <int>self.nextUInt64DoubleBound(start, end)

