cpdef createFalloffEvaluator(falloff, str sourceType)

cdef class FalloffEvaluator:
    cdef double evaluate(self, void* value, long index)
