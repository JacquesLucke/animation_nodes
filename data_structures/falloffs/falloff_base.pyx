cdef class Falloff:
    pass


cdef class BaseFalloff(Falloff):

    cdef double evaluate(BaseFalloff self, void* object, long index):
        raise NotImplementedError()


cdef class CompoundFalloff(Falloff):

    cdef list getDependencies(self):
        raise NotImplementedError()

    cdef double evaluate(self, double* dependencyResults):
        raise NotImplementedError()
