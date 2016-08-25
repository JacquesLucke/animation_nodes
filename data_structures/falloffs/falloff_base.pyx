cdef class FalloffBase:

    cpdef getHandledDataType(self):
        raise NotImplementedError()

    cdef double evaluate(FalloffBase self, void* object, long index):
        raise NotImplementedError()
