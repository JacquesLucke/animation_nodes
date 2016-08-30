ctypedef fused list_or_tuple:
    list
    tuple

cdef class IntegerList:
    cdef:
        int* data
        Py_ssize_t length
        Py_ssize_t capacity

    cdef grow(self, Py_ssize_t minCapacity)
    cdef void shrinkToLength(self)
    cdef replaceArray(self, int* newData, Py_ssize_t newLength, Py_ssize_t newCapacity)

    cpdef copy(self)
    cpdef clear(self)
    cpdef fill(self, value)

    cpdef append(self, value)
    cpdef extend(self, values)
    cdef extendList(self, list values)
    cdef extendTuple(self, tuple values)
    cpdef remove(self, value)
    cpdef index(self, value)
    cdef Py_ssize_t searchIndex(self, int value)
    cpdef count(self, value)
    cpdef insert(self, Py_ssize_t index, value)

    cpdef getMemoryView(self)

    cdef IntegerList getValuesInSlice(self, slice sliceObject)
    cdef setValuesInSlice(self, slice sliceObject, values)
    cdef removeValuesInSlice(self, slice sliceObject)

    cdef setValuesInSimpleSlice(self, Py_ssize_t start, Py_ssize_t stop, values)
    cdef setValuesInExtendedSlice(self, Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step, values)

    cdef getValueAtIndex(self, Py_ssize_t index)
    cdef setValueAtIndex(self, Py_ssize_t index, int value)
    cdef removeValueAtIndex(self, Py_ssize_t index)



    cpdef IntegerList reversed(self)
    cdef overwrite(self, IntegerList other, Py_ssize_t index = ?)
    cdef overwriteArray(self, int* array, Py_ssize_t arrayLength, Py_ssize_t index)

    # Helpers
    cdef tryConversion(self, value, int* target)
    cdef equals_SameType(self, IntegerList other)
    cdef tryCorrectIndex(self, Py_ssize_t index)
