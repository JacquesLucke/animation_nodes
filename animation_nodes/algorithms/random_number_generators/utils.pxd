from libc.stdint cimport uint64_t

cdef inline uint64_t rotl(uint64_t x, uint64_t k):
    return (x << k) | (x >> (<uint64_t>64 - k))
