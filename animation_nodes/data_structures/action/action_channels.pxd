from . action_base cimport ActionChannel

cdef class PathActionChannel(ActionChannel):
    cdef readonly str path

cdef class PathIndexActionChannel(ActionChannel):
    cdef readonly str property
    cdef readonly Py_ssize_t index
