from . falloff_base cimport Falloff

cpdef createFalloffEvaluator(Falloff falloff, str sourceType, bint clamped = ?)

cdef class FalloffEvaluator:
    cdef double evaluate(self, void* value, long index)
