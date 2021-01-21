from ... data_structures cimport (
    DoubleList,
    VirtualDoubleList
)

def executeSubtract_A_B(VirtualDoubleList a, VirtualDoubleList b, long amount):
    cdef DoubleList result = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        result.data[i] = a.get(i) - b.get(i)
    return result

