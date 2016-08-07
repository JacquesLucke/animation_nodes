from . base_lists cimport UIntegerList, IntegerList

cdef class PolygonIndicesList:
    cdef:
        readonly UIntegerList indices
        readonly IntegerList loopStarts
        readonly IntegerList loopLengths

    cdef long getLength(self)

    cpdef append(self, value)
    cpdef extend(self, values)

    cdef isValueValid(self, value)
