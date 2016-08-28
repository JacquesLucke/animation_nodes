cdef class Falloff:
    def __cinit__(self):
        self.clamped = False


cdef class BaseFalloff(Falloff):

    cdef double evaluate(BaseFalloff self, void* object, long index):
        raise NotImplementedError()


cdef class CompoundFalloff(Falloff):
    def __cinit__(self):
        self.requiresClampedInput = False

    cdef list getDependencies(self):
        raise NotImplementedError()

    cdef double evaluate(self, double* dependencyResults):
        raise NotImplementedError()
