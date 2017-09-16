cdef class FalloffEvaluator:
    '''The evaluator of a falloff is only valid while the falloff exists'''
    cdef object pyEvaluator

    cdef float evaluate(self, void *value, Py_ssize_t index)
