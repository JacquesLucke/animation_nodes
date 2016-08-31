from . conversion cimport toMatrix4
from . cimport (transformVec3AsPoint_InPlace, transformVec3AsDirection_InPlace,
                distanceVec3, mixVec3, multMatrix4, setIdentityMatrix4)


cpdef void transformVector3DList(Vector3DList vectors, matrix, bint ignoreTranslation = False):
    cdef Matrix4 _matrix = toMatrix4(matrix)
    transformVector3DListAsPoints(vectors.base.data, vectors.length, &_matrix, ignoreTranslation)

cdef void transformVector3DListAsPoints(Vector3* vectors, long arrayLength, Matrix4* matrix, bint ignoreTranslation):
    cdef long i
    if ignoreTranslation:
        for i in range(arrayLength):
            transformVec3AsDirection_InPlace(vectors + i, matrix)
    else:
        for i in range(arrayLength):
            transformVec3AsPoint_InPlace(vectors + i, matrix)


cpdef double distanceSumOfVector3DList(Vector3DList vectors):
    cdef:
        double distance = 0
        long i

    for i in range(vectors.getLength() - 1):
        distance += distanceVec3(vectors.data + i, vectors.data + i + 1)
    return distance

cdef void mixVec3Arrays(Vector3* target, Vector3* a, Vector3* b, long arrayLength, float factor):
    cdef long i
    for i in range(arrayLength):
        mixVec3(target + i, a + i, b + i, factor)

cdef void reduceMatrix4x4List(Matrix4* matrices, unsigned long amount, Matrix4* target):
    cdef:
        long i
        Matrix4 tmp

    if amount == 0:
        setIdentityMatrix4(target)
    elif amount == 1:
        target[0] = matrices[0]
    else:
        tmp = matrices[0]
        for i in range(1, amount):
            multMatrix4(target, &tmp, matrices + i)
            tmp = target[0]
