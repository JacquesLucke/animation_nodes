cdef class FalloffBase:

    cpdef getHandledDataType(self)

    cdef double execute(self, void* object, long index)
