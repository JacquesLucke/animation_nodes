from . base_lists cimport UIntegerList, ULongList

cdef class PolygonIndicesList:
    cdef:
        readonly UIntegerList indices
        readonly UIntegerList loopStarts
        readonly UIntegerList loopLengths

    cdef long getLength(self)

    cpdef append(self, value)
    cpdef extend(self, values)
    cpdef copy(self)

    cdef getElementAtIndex(self, long index)
    cdef getValuesInSlice(self, slice sliceObject)

    cpdef copyWithNewOrder(self, ULongList newOrder, checkIndices = ?)

    cdef isValueValid(self, value)
    cdef tryCorrectIndex(self, long index)
