from . evaluation cimport FalloffEvaluator

cdef class Falloff:
    cdef bint clamped
    cdef dict evaluators

    cpdef FalloffEvaluator getEvaluator(self, str sourceType, bint clamped = ?)

cdef class BaseFalloff(Falloff):
    cdef str dataType
    cdef float evaluate(self, void *object, Py_ssize_t index)
    cdef void evaluateList(self, void *objects, Py_ssize_t startIndex,
                           Py_ssize_t amount, float *target)

cdef class CompoundFalloff(Falloff):
    cdef list getDependencies(self)
    cdef list getClampingRequirements(self)
    cdef float evaluate(self, float *dependencyResults)
    cdef void evaluateList(self, float **dependencyResults, Py_ssize_t amount, float *target)
