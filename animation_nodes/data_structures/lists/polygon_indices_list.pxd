from . base_lists cimport UIntegerList, ULongList

cdef class PolygonIndicesList:
    cdef:
        readonly UIntegerList indices
        readonly UIntegerList polyStarts
        readonly UIntegerList polyLengths

    cdef long getLength(self)

    cpdef append(self, value)
    cpdef extend(self, values)
    cpdef copy(self)

    cdef getElementAtIndex(self, long index)
    cdef getValuesInSlice(self, slice sliceObject)

    cpdef copyWithNewOrder(self, ULongList newOrder, checkIndices = ?)
    cdef extend_SameType(self, PolygonIndicesList otherList)

    cdef isValueValid(self, value)
    cdef tryCorrectIndex(self, long index)
