cpdef void transformVector3DList(Vector3DList vectors, matrix):
    cdef:
        Matrix4 _matrix
        Vector3* _vectors

    toMatrix4(&_matrix, matrix)
    _vectors = <Vector3*>vectors.base.data
    transformVector3DList_lowlevel(_vectors, vectors.getLength(), &_matrix)

cdef void transformVector3DList_lowlevel(Vector3* vectors, long arrayLength, Matrix4* matrix):
    cdef long i
    for i in range(arrayLength):
        transformVec3(vectors + i, vectors + i, matrix)

cpdef double distanceSumOfVector3DList(Vector3DList vectors):
    cdef:
        Vector3* _vectors = <Vector3*>vectors.base.data
        double distance = 0
        long i

    for i in range(vectors.getLength() - 1):
        distance += distanceVec3(_vectors + i, _vectors + i + 1)
    return distance
