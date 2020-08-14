from .. math cimport Vector3
from .. data_structures cimport Vector3DList, Matrix4x4List, IntegerList

def getMatricesVBOandIBO(Matrix4x4List matrices, float scaleX, float scaleY, float scaleZ):
    cdef Py_ssize_t i
    cdef int length = len(matrices)
    cdef Vector3DList vectors = Vector3DList(length = length * 4)
    cdef IntegerList indices = IntegerList(length = length * 6)
    cdef float x, y, z
    for i in range(length):
        x, y, z = matrices.data[i].a14, matrices.data[i].a24, matrices.data[i].a34
        vectors.data[i * 4] = Vector3(x, y, z)
        vectors.data[i * 4 + 1] = Vector3(
            x + matrices.data[i].a11 * scaleX,
            y + matrices.data[i].a21 * scaleX,
            z + matrices.data[i].a31 * scaleX)
        vectors.data[i * 4 + 2] = Vector3(
            x + matrices.data[i].a12 * scaleY,
            y + matrices.data[i].a22 * scaleY,
            z + matrices.data[i].a32 * scaleY)
        vectors.data[i * 4 + 3] = Vector3(
            x + matrices.data[i].a13 * scaleZ,
            y + matrices.data[i].a23 * scaleZ,
            z + matrices.data[i].a33 * scaleZ)
        indices.data[i * 6] = i * 4
        indices.data[i * 6 + 1] = i * 4 + 1
        indices.data[i * 6 + 2] = i * 4
        indices.data[i * 6 + 3] = i * 4 + 2
        indices.data[i * 6 + 4] = i * 4
        indices.data[i * 6 + 5] = i * 4 + 3
    return vectors, indices
