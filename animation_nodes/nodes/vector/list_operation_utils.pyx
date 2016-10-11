from ... data_structures cimport DoubleList, Vector3DList

def combineDoubleListsToVectorList(DoubleList x, DoubleList y, DoubleList z):
    assert x.length == y.length == z.length
    cdef Vector3DList output = Vector3DList(length = len(x))
    cdef long i
    for i in range(len(output)):
        output.data[i].x = x.data[i]
        output.data[i].y = y.data[i]
        output.data[i].z = z.data[i]
    return output
