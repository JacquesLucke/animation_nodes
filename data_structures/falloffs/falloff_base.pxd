cdef class FalloffBase:
    cdef str dataType

    cdef double evaluate(self, void* object, long index)
