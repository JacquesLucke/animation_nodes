cdef class Falloff:
    def __cinit__(self):
        self.clamped = False
        self.evaluators = dict()

    cpdef FalloffEvaluator getEvaluator(self, str sourceType, bint clamped = False, bint onlyC = False):
        settings = (sourceType, clamped, onlyC)
        if settings not in self.evaluators:
            self.evaluators[settings] = FalloffEvaluator.create(self, sourceType, clamped, onlyC)
        return self.evaluators[settings]


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
