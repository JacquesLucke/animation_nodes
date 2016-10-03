cdef class FalloffEvaluator:
    # create using FalloffEvaluator.create(falloff, sourceType, clamped)
    cdef double evaluate(self, void* value, long index)
