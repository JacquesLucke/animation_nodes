cdef class FalloffBase:

    def getHandledDataType(self):
        raise NotImplementedError()

    cdef double execute(FalloffBase self, void* object, long index):
        raise NotImplementedError()
