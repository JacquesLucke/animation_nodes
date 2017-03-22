cimport cython

@cython.freelist(10)
cdef class CList:
    cdef void* getPointer(self):
        raise NotImplementedError()

    cdef int getElementSize(self):
        raise NotImplementedError()

    cdef Py_ssize_t getLength(self):
        raise NotImplementedError()

    cdef Py_ssize_t getCapacity(self):
        raise NotImplementedError()
