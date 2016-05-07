from .. data_structures.lists.base_lists cimport DoubleList, FloatList, LongLongList

def createDoubleListRange(long amount, double start, double step):
    cdef DoubleList newList = DoubleList(max(0, amount))
    cdef long i
    for i in range(max(0, amount)):
        newList.data[i] = start + i * step
    return newList

def createLongLongListRange(long amount, double start, double step):
    cdef LongLongList newList = LongLongList(max(0, amount))
    cdef long i
    for i in range(max(0, amount)):
        newList.data[i] = <long long>(start + i * step)
    return newList
