cdef class FalloffEvaluator:
    cdef object pyEvaluator

    cdef double evaluate(self, void* value, long index)
