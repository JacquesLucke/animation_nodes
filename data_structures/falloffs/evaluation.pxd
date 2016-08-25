from . falloff_base cimport FalloffBase

cdef class FalloffEvaluator:

    cdef:
        readonly bint isValid

    cdef double evaluate(self, void* value, long index)

cdef class FalloffBaseEvaluator(FalloffEvaluator):
    cdef:
        FalloffBase falloff


cpdef getFalloffEvaluator(falloff, str sourceType)
