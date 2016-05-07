from ... data_structures.lists.base_lists cimport DoubleList, FloatList, LongLongList

cpdef DoubleList FloatList_to_DoubleList(FloatList sourceList):
    cdef DoubleList newList = DoubleList(sourceList.length)
    cdef long i
    for i in range(len(sourceList)):
        newList.data[i] = sourceList.data[i]
    return newList

cpdef DoubleList LongLongList_to_DoubleList(LongLongList sourceList):
    cdef DoubleList newList = DoubleList(sourceList.length)
    cdef long i
    for i in range(len(sourceList)):
        newList.data[i] = sourceList.data[i]
    return newList

cpdef LongLongList DoubleList_to_LongLongList(DoubleList sourceList):
    cdef LongLongList newList = LongLongList(sourceList.length)
    cdef long i
    for i in range(len(sourceList)):
        newList.data[i] = <long long>sourceList.data[i]
    return newList
