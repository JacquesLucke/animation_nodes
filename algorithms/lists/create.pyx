from libc.limits cimport LONG_MAX
from ... data_structures.lists.base_lists cimport DoubleList, FloatList, LongLongList, UShortList

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

def getMinValue(LongLongList source):
    if source.length == 0:
        raise Exception("List is empty")

    cdef long long minValue = LONG_MAX
    cdef long i
    for i in range(source.length):
        if source.data[i] < minValue:
            minValue = source.data[i]
    return minValue
