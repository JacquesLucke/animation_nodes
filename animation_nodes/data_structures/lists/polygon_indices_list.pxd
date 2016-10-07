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
    cpdef index(self, value)
    cpdef count(self, value)

    cdef getElementAtIndex(self, long index)
    cdef getValuesInSlice(self, slice sliceObject)

    cdef setElementAtIndex(self, long index, value)
    cdef setElementAtIndex_SameLength(self, long index, value)
    cdef setElementAtIndex_DifferentLength(self, long index, value)

    cpdef copyWithNewOrder(self, ULongList newOrder, checkIndices = ?)
    cdef extend_SameType(self, PolygonIndicesList otherList)

    cdef isValueValid(self, value)
    cdef tryCorrectIndex(self, long index)
