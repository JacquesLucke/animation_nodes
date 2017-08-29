cdef class Action:
    cdef set getChannelSet(self)

cdef class ActionEvaluator:
    cdef Py_ssize_t channelAmount

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target)

cdef class ActionChannel:
    pass
