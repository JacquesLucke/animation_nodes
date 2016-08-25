cdef class FalloffBase:

    cpdef getHandledDataType(self):
        raise NotImplementedError()

    cdef double execute(FalloffBase self, void* object, long index):
        raise NotImplementedError()
