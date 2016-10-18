from . conversion cimport toMatrix4
from . vector cimport distanceVec3, mixVec3
from . matrix cimport (transformVec3AsPoint_InPlace, transformVec3AsDirection_InPlace,
                       multMatrix4, setIdentityMatrix, setComposedMatrix)


cpdef void transformVector3DList(Vector3DList vectors, matrix, bint ignoreTranslation = False):
    cdef Matrix4 _matrix = toMatrix4(matrix)
    transformVector3DListAsPoints(vectors.data, vectors.length, &_matrix, ignoreTranslation)

cdef void transformVector3DListAsPoints(Vector3* vectors, long arrayLength, Matrix4* matrix, bint ignoreTranslation):
    cdef long i
    if ignoreTranslation:
        for i in range(arrayLength):
            transformVec3AsDirection_InPlace(vectors + i, matrix)
    else:
        for i in range(arrayLength):
            transformVec3AsPoint_InPlace(vectors + i, matrix)


cpdef Matrix4x4List composeMatrixList(Vector3DList locations, EulerList rotations, Vector3DList scales):
    if not (len(locations) == len(rotations) == len(scales)):
        raise ValueError("lists have different lengths")
    cdef:
        Matrix4x4List newList = Matrix4x4List(length = len(locations))
        size_t i

    for i in range(len(locations)):
        setComposedMatrix(newList.data + i, locations.data + i, rotations.data + i, scales.data + i)
    return newList


cpdef double distanceSumOfVector3DList(Vector3DList vectors):
    cdef:
        double distance = 0
        long i

    for i in range(vectors.length - 1):
        distance += distanceVec3(vectors.data + i, vectors.data + i + 1)
    return distance

cdef void mixVec3Arrays(Vector3* target, Vector3* a, Vector3* b, long arrayLength, float factor):
    cdef long i
    for i in range(arrayLength):
        mixVec3(target + i, a + i, b + i, factor)

cdef void reduceMatrix4x4List(Matrix4* matrices, unsigned long amount, Matrix4* target, bint reversed = False):
    cdef:
        long i
        Matrix4 tmp

    if amount == 0:
        setIdentityMatrix(target)
    elif amount == 1:
        target[0] = matrices[0]
    else:
        if reversed:
            tmp = matrices[amount - 1]
            for i in range(amount - 2, -1, -1):
                multMatrix4(target, &tmp, matrices + i)
                tmp = target[0]
        else:
            tmp = matrices[0]
            for i in range(1, amount):
                multMatrix4(target, &tmp, matrices + i)
                tmp = target[0]

def scaleVector3DList(Vector3DList vectors, float factor):
    cdef Vector3* data = vectors.data
    cdef long i
    for i in range(vectors.length):
        data[i].x *= factor
        data[i].y *= factor
        data[i].z *= factor
