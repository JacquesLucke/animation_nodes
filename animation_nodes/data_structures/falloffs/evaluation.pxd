from . types cimport FalloffSourceType

cdef class FalloffEvaluator:
    cdef FalloffSourceType sourceType

    cdef float evaluate(self, void *value, Py_ssize_t index)
    cdef pyEvaluate(self, object value, Py_ssize_t index)
