from ... math cimport Vector3, distanceVec3, lengthVec3, dotVec3
from ... data_structures cimport (
    DoubleList, Vector3DList, CDefaultList, Vector2DList,
    VirtualDoubleList, VirtualVector3DList, FloatList)

def combineVectorList(Py_ssize_t amount,
                      VirtualDoubleList x, VirtualDoubleList y, VirtualDoubleList z):
    cdef Vector3DList output = Vector3DList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        output.data[i].x = <float>x.get(i)
        output.data[i].y = <float>y.get(i)
        output.data[i].z = <float>z.get(i)
    return output

def getAxisListOfVectorList(Vector3DList myList, str axis):
    assert axis in "xyz"
    cdef DoubleList output = DoubleList(length = myList.length)
    cdef Py_ssize_t i
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
    cdef Py_ssize_t i
    for i in range(values.length):
        output.data[i].x = <float>values.data[i]
        output.data[i].y = <float>values.data[i]
        output.data[i].z = <float>values.data[i]
    return output

def calculateVectorDistancesVirtual(int amount,
                             VirtualVector3DList vectors1,
                             VirtualVector3DList vectors2):
    cdef DoubleList distances = DoubleList(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        distances.data[i] = distanceVec3(vectors1.get(i), vectors2.get(i))

    return distances

def calculateVectorDistances(Vector3DList vectors1, Vector3DList vectors2):
    cdef DoubleList distances = DoubleList(length = len(vectors1))
    cdef Py_ssize_t i

    for i in range(len(vectors1)):
        distances.data[i] = distanceVec3(vectors1.data + i, vectors2.data + i)

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

def convert_Vector3DList_to_Vector2DList(Vector3DList vectors):
    cdef Py_ssize_t i
    cdef Vector2DList vectors2D = Vector2DList(length = len(vectors))
    for i in range(len(vectors)):
        vectors2D.data[i].x = vectors.data[i].x
        vectors2D.data[i].y = vectors.data[i].y
    return vectors2D

def convert_Vector2DList_to_Vector3DList(Vector2DList vectors):
    cdef Py_ssize_t i
    cdef Vector3DList vectors3D = Vector3DList(length = len(vectors))
    for i in range(len(vectors)):
        vectors3D.data[i].x = vectors.data[i].x
        vectors3D.data[i].y = vectors.data[i].y
        vectors3D.data[i].z = <float>0.0
    return vectors3D

def offset3DVectors(Vector3DList vectors, VirtualVector3DList offsets, FloatList influences):
    cdef Vector3 *offset
    cdef float influence
    cdef Py_ssize_t i

    for i in range(len(vectors)):
        influence = influences.data[i]
        offset = offsets.get(i)
        vectors.data[i].x += offset.x * influence
        vectors.data[i].y += offset.y * influence
        vectors.data[i].z += offset.z * influence

def calculateVectorDotProducts(Py_ssize_t amount,
                        VirtualVector3DList vectors1,
                        VirtualVector3DList vectors2):
    cdef Py_ssize_t i
    cdef DoubleList dotProducts = DoubleList(length = amount)
    for i in range(amount):
        dotProducts.data[i] = dotVec3(vectors1.get(i), vectors2.get(i))
    return dotProducts
