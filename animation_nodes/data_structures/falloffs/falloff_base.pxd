from . evaluation cimport FalloffEvaluator

cdef class Falloff:
    cdef bint clamped
    cdef dict evaluators

    cpdef FalloffEvaluator getEvaluator(self, str sourceType, bint clamped = ?, bint onlyC = ?)

cdef class BaseFalloff(Falloff):
    cdef str dataType
    cdef float evaluate(self, void *object, Py_ssize_t index)

cdef class CompoundFalloff(Falloff):
    cdef list getDependencies(self)
    cdef list getClampingRequirements(self)
    cdef float evaluate(self, float *dependencyResults)
