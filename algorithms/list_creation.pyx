from .. data_structures.lists.base_lists cimport DoubleList, FloatList

def fromRange(long amount, double start, double step):
    cdef DoubleList newList = DoubleList(max(0, amount))
    cdef long i
    for i in range(max(0, amount)):
        newList.data[i] = start + i * step
    return newList

cpdef DoubleList floatListToDoubleList(FloatList floatList):
    cdef DoubleList newList = DoubleList(floatList.length)
    cdef long i
    for i in range(len(floatList)):
        newList.data[i] = floatList.data[i]
    return newList
