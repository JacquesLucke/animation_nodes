cdef class Falloff:
    def __cinit__(self):
        self.clamped = False
        self.evaluators = dict()

    cpdef FalloffEvaluator getEvaluator(self, str sourceType, bint clamped = False):
        settings = (sourceType, clamped)
        if settings not in self.evaluators:
            self.evaluators[settings] = FalloffEvaluator.create(self, sourceType, clamped)
        return self.evaluators[settings]


cdef class BaseFalloff(Falloff):

    cdef float evaluate(self, void *object, Py_ssize_t index):
        raise NotImplementedError()

    def __repr__(self):
        return "{}".format(type(self).__name__)


cdef class CompoundFalloff(Falloff):
    cdef list getDependencies(self):
        raise NotImplementedError()

    cdef list getClampingRequirements(self):
        return [False] * len(self.getDependencies())

    cdef float evaluate(self, float *dependencyResults):
        raise NotImplementedError()

    def __repr__(self):
        return "\n".join(self._iterReprLines())

    def _iterReprLines(self):
        yield "{}:".format(type(self).__name__)
        for falloff in self.getDependencies():
            for line in str(falloff).splitlines():
                yield "  " + line
