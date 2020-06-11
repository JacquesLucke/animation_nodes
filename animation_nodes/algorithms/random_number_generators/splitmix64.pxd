from libc.stdint cimport uint64_t

# Based on http://prng.di.unimi.it/splitmix64.c

cdef class SplitMix64:
    cdef uint64_t x

    cdef uint64_t nextUInt64(self)
