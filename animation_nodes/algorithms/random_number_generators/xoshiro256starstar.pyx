from . utils cimport rotl
from . cimport SplitMix64
from libc.stdint cimport uint64_t
from . cimport RandomNumberGenerator

# Based on http://prng.di.unimi.it/xoshiro256starstar.c

cdef class XoShiRo256StarStar(RandomNumberGenerator):
    def __cinit__(self, uint64_t seed):
        cdef SplitMix64 rng = SplitMix64(seed)
        self.s0 = rng.nextUInt64()
        self.s1 = rng.nextUInt64()
        self.s2 = rng.nextUInt64()
        self.s3 = rng.nextUInt64()

    cdef uint64_t nextUInt64(self):
        cdef uint64_t result = rotl(self.s1 * <uint64_t>5, <uint64_t>7) * <uint64_t>9

        cdef uint64_t t = self.s1 << <uint64_t>17

        self.s2 ^= self.s0
        self.s3 ^= self.s1
        self.s1 ^= self.s2
        self.s0 ^= self.s3

        self.s2 ^= t

        self.s3 = rotl(self.s3, <uint64_t>45)

        return result
