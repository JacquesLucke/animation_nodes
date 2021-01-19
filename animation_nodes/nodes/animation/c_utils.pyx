from ... data_structures cimport (
    LongList,
    DoubleList,
    VirtualDoubleList
)

def delayTime_Multiple(VirtualDoubleList a, VirtualDoubleList b, long amount):
    cdef DoubleList result = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        result.data[i] = a.get(i) - b.get(i)
    return result