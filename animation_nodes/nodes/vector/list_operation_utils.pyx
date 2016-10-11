from ... data_structures cimport DoubleList, Vector3DList

def combineDoubleListsToVectorList(DoubleList x, DoubleList y, DoubleList z):
    assert x.length == y.length == z.length
    cdef Vector3DList output = Vector3DList(length = x.length)
    cdef long i
    for i in range(output.length):
        output.data[i].x = x.data[i]
        output.data[i].y = y.data[i]
        output.data[i].z = z.data[i]
    return output

def getAxisListOfVectorList(Vector3DList myList, str axis):
    assert axis in "xyz"
    cdef DoubleList output = DoubleList(length = myList.length)
    cdef long i
    if axis == "x":
        for i in range(output.length):
            output.data[i] = myList.data[i].x
    elif axis == "y":
        for i in range(output.length):
            output.data[i] = myList.data[i].y
    elif axis == "z":
        for i in range(output.length):
            output.data[i] = myList.data[i].z
    return output
