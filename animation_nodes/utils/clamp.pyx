from libc.limits cimport INT_MAX, INT_MIN, LONG_MAX, LONG_MIN

cdef int clampInt(object value):
    return max(INT_MIN, min(INT_MAX, value))

cdef int clampLong(object value):
    return max(LONG_MIN, min(LONG_MAX, value))
