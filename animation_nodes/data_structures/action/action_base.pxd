from .. lists.base_lists cimport FloatList, IntegerList

cdef class Action:
    cdef readonly set channels

cdef class BoundedAction(Action):
    cdef BoundedActionEvaluator getEvaluator_Limited(self, list channels)
    cpdef BoundedActionEvaluator getEvaluator_Full(self, list channels, FloatList defaults)

cdef class UnboundedAction(Action):
    cdef UnboundedActionEvaluator getEvaluator_Limited(self, list channels)
    cpdef UnboundedActionEvaluator getEvaluator_Full(self, list channels, FloatList defaults)


cdef class ActionEvaluator:
    cdef Py_ssize_t channelAmount

    cdef void evaluate(self, float frame, Py_ssize_t index, float *target)

cdef class UnboundedActionEvaluator(ActionEvaluator):
    pass

cdef class BoundedActionEvaluator(ActionEvaluator):
    cdef void evaluateBounded(self, float t, Py_ssize_t index, float *target)

    cpdef float getStart(self, Py_ssize_t index)
    cpdef float getEnd(self, Py_ssize_t index)
    cpdef float getLength(self, Py_ssize_t index)


cdef class ActionChannel:
    pass

cdef class PathActionChannel(ActionChannel):
    cdef readonly str path

cdef class PathIndexActionChannel(PathActionChannel):
    cdef readonly Py_ssize_t index
