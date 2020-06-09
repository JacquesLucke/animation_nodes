from libc.stdint cimport uint64_t
from . cimport RandomNumberGenerator

# Based on http://prng.di.unimi.it/splitmix64.c

cdef class SplitMix64(RandomNumberGenerator):
    cdef uint64_t x
