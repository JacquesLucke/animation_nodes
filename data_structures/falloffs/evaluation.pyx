cdef class FalloffEvaluator:
    cdef double evaluate(self, void* value, long index):
        raise NotImplementedError()

cdef class FalloffBaseEvaluator(FalloffEvaluator):
    def __cinit__(self, FalloffBase falloff, str sourceType):
        cdef str dataType = falloff.getHandledDataType()
        self.isValid = dataType == "All" or sourceType == dataType
        if self.isValid:
            self.falloff = falloff

    cdef double evaluate(self, void* value, long index):
        return self.falloff.evaluate(value, index)


cpdef getFalloffEvaluator(falloff, str sourceType):
    cdef FalloffEvaluator evaluator

    if isinstance(falloff, FalloffBase):
        evaluator = FalloffBaseEvaluator(falloff, sourceType)

    if getattr(evaluator, "isValid", False):
        return evaluator
    return None
