cdef class FalloffBase:
    cdef double evaluate(FalloffBase self, void* object, long index):
        raise NotImplementedError()
