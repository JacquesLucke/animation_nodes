cdef class FalloffEvaluator:
    cdef str sourceType

    cdef float evaluate(self, void *value, Py_ssize_t index)
    cdef pyEvaluate(self, object value, Py_ssize_t index)

    cdef void evaluateList_LowLevel(self, void *values, Py_ssize_t startIndex,
                                    Py_ssize_t amount, float *target)
