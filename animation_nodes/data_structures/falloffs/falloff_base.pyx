cdef dict evaluatorsCache = dict()

cdef class Falloff:
    def __cinit__(self):
        self.clamped = False

    def __dealloc__(self):
        if hash(self) in evaluatorsCache:
            del evaluatorsCache[hash(self)]

    cpdef FalloffEvaluator getEvaluator(self, str sourceType, bint clamped = False, bint onlyC = False):
        cdef FalloffEvaluator evaluator
        falloffHash = hash(self)
        settings = (sourceType, clamped, onlyC)

        if falloffHash in evaluatorsCache:
            subCache = evaluatorsCache[falloffHash]
            if settings in subCache:
                return subCache[settings]
            evaluator = FalloffEvaluator.create(self, sourceType, clamped, onlyC)
            subCache[settings] = evaluator
        else:
            evaluator = FalloffEvaluator.create(self, sourceType, clamped, onlyC)
            evaluatorsCache[falloffHash] = {settings : evaluator}
        return evaluator


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
