from libc.stdint cimport uint64_t

# Based on http://prng.di.unimi.it/splitmix64.c

cdef class SplitMix64:
    def __cinit__(self, uint64_t seed):
        self.x = seed

    cdef uint64_t nextUInt64(self):
        self.x += <uint64_t>0x9e3779b97f4a7c15
        cdef uint64_t z = self.x
        z = (z ^ (z >> <uint64_t>30)) * <uint64_t>0xbf58476d1ce4e5b9
        z = (z ^ (z >> <uint64_t>27)) * <uint64_t>0x94d049bb133111eb
        return z ^ (z >> <uint64_t>31)
