cdef class FalloffBase:

    cpdef getHandledDataType(self)

    cdef double evaluate(self, void* object, long index)
