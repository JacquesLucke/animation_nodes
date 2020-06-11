from . utils cimport rotl
from . cimport SplitMix64
from libc.stdint cimport uint64_t

# Based on http://prng.di.unimi.it/xoshiro256plus.c

cdef class XoShiRo256Plus:
    def __cinit__(self, uint64_t seed):
        cdef SplitMix64 rng = SplitMix64(seed)
        self.s0 = rng.nextUInt64()
        self.s1 = rng.nextUInt64()
        self.s2 = rng.nextUInt64()
        self.s3 = rng.nextUInt64()

    cdef uint64_t nextUInt64(self):
        cdef uint64_t result = self.s0 + self.s3

        cdef uint64_t t = self.s1 << <uint64_t>17

        self.s2 ^= self.s0
        self.s3 ^= self.s1
        self.s1 ^= self.s2
        self.s0 ^= self.s3

        self.s2 ^= t

        self.s3 = rotl(self.s3, <uint64_t>45)

        return result

    cdef double nextDouble(self):
        cdef uint64_t x = (<uint64_t>0x3FF << <uint64_t>52) | (self.nextUInt64() >> <uint64_t>12)
        return (<double *>(&x))[0] - <double>1.0

    cdef float nextFloat(self):
        cdef uint64_t x = <uint64_t>0x3F800000 | (<uint64_t>0x007FFFFF & self.nextUInt64())
        return (<float *>(&x))[0] - <float>1.0
