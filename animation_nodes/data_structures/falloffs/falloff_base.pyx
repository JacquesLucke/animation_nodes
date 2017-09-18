from libc.stdlib cimport malloc, free
from . types cimport getSizeOfFalloffDataType

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

    cdef void evaluateList(self, void *objects, Py_ssize_t startIndex,
                           Py_ssize_t amount, float *target):
        cdef Py_ssize_t i
        cdef Py_ssize_t elementSize = getSizeOfFalloffDataType(self.dataType)
        for i in range(amount):
            target[i] = self.evaluate(<char*>objects + i * elementSize, i + startIndex)

    def __repr__(self):
        return "{}".format(type(self).__name__)


cdef class CompoundFalloff(Falloff):
    cdef list getDependencies(self):
        raise NotImplementedError()

    cdef list getClampingRequirements(self):
        return [False] * len(self.getDependencies())

    cdef float evaluate(self, float *dependencyResults):
        raise NotImplementedError()

    cdef void evaluateList(self, float **dependencyResults, Py_ssize_t amount, float *target):
        cdef Py_ssize_t i, j
        cdef Py_ssize_t depsAmount = len(self.getDependencies())
        cdef float *buffer = <float*>malloc(sizeof(float) * depsAmount)

        for i in range(amount):
            for j in range(depsAmount):
                buffer[j] = dependencyResults[j][i]
            target[i] = self.evaluate(buffer)

        free(buffer)


    def __repr__(self):
        return "\n".join(self._iterReprLines())

    def _iterReprLines(self):
        yield "{}:".format(type(self).__name__)
        for falloff in self.getDependencies():
            for line in str(falloff).splitlines():
                yield "  " + line
