from libc.stdint cimport uint64_t
from . cimport RandomNumberGenerator

cdef class XoShiRo256StarStar(RandomNumberGenerator):
    cdef uint64_t s0
    cdef uint64_t s1
    cdef uint64_t s2
    cdef uint64_t s3
