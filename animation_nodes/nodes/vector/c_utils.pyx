from ... math cimport Vector3, distanceVec3, lengthVec3
from ... data_structures cimport (
    DoubleList, Vector3DList, CDefaultList,
    VirtualDoubleList)

def combineVectorList(Py_ssize_t amount,
                      VirtualDoubleList x, VirtualDoubleList y, VirtualDoubleList z):
    cdef Vector3DList output = Vector3DList(length = amount)
    cdef long i
    for i in range(amount):
        output.data[i].x = <float>x.get(i)
        output.data[i].y = <float>y.get(i)
        output.data[i].z = <float>z.get(i)
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

def vectorsFromValues(DoubleList values):
    cdef Vector3DList output = Vector3DList(length = values.length)
    cdef long i
    for i in range(values.length):
        output.data[i].x = <float>values.data[i]
        output.data[i].y = <float>values.data[i]
        output.data[i].z = <float>values.data[i]
    return output

def calculateVectorDistances(_vectors1, _vectors2):
    cdef:
        CDefaultList vectors1 = CDefaultList(Vector3DList, _vectors1, (0, 0, 0))
        CDefaultList vectors2 = CDefaultList(Vector3DList, _vectors2, (0, 0, 0))
        Py_ssize_t amount = CDefaultList.getMaxLength(vectors1, vectors2)
        DoubleList distances = DoubleList(length = amount)
        Py_ssize_t i

    for i in range(amount):
        distances.data[i] = distanceVec3(<Vector3*>vectors1.get(i), <Vector3*>vectors2.get(i))

    return distances

def calculateVectorLengths(Vector3DList vectors):
    cdef Py_ssize_t i
    cdef DoubleList lengths = DoubleList(length = len(vectors))
    for i in range(len(vectors)):
        lengths.data[i] = lengthVec3(vectors.data + i)
    return lengths

def calculateVectorCenters(Vector3DList vectors1, Vector3DList vectors2):
    assert len(vectors1) == len(vectors2)

    cdef Vector3DList centers = Vector3DList(length = len(vectors1))
    cdef Py_ssize_t i

    for i in range(len(vectors1)):
        centers.data[i].x = (vectors1.data[i].x + vectors2.data[i].x) * <float>0.5
        centers.data[i].y = (vectors1.data[i].y + vectors2.data[i].y) * <float>0.5
        centers.data[i].z = (vectors1.data[i].z + vectors2.data[i].z) * <float>0.5

    return centers
