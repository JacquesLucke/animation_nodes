cdef class Falloff:
    def __cinit__(self):
        self.clamped = False

    cpdef FalloffEvaluator getEvaluator(self, str sourceType, bint clamped = False):
        return FalloffEvaluator.create(self, sourceType, clamped)


cdef class BaseFalloff(Falloff):

    cdef double evaluate(BaseFalloff self, void* object, long index):
        raise NotImplementedError()


cdef class CompoundFalloff(Falloff):
    cdef list getDependencies(self):
        raise NotImplementedError()

    cdef list getClampingRequirements(self):
        return [False] * len(self.getDependencies())

    cdef double evaluate(self, double* dependencyResults):
        raise NotImplementedError()
