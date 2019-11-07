from .. math cimport Vector3
from .. data_structures cimport Vector3DList, Matrix4x4List, IntegerList

def getMatricesVBOandIBO(Matrix4x4List matrices, float scale):
    cdef Py_ssize_t i
    cdef int length = len(matrices)
    cdef Vector3DList vectors = Vector3DList(length = length * 4)
    cdef IntegerList indices = IntegerList(length = length * 6)
    cdef float x, y, z
    for i in range(length):
        x, y, z = matrices.data[i].a14, matrices.data[i].a24, matrices.data[i].a34
        vectors.data[i * 4] = Vector3(x, y, z)
        vectors.data[i * 4 + 1] = Vector3(
            x + matrices.data[i].a11 * scale,
            y + matrices.data[i].a21 * scale,
            z + matrices.data[i].a31 * scale)
        vectors.data[i * 4 + 2] = Vector3(
            x + matrices.data[i].a12 * scale,
            y + matrices.data[i].a22 * scale,
            z + matrices.data[i].a32 * scale)
        vectors.data[i * 4 + 3] = Vector3(
            x + matrices.data[i].a13 * scale,
            y + matrices.data[i].a23 * scale,
            z + matrices.data[i].a33 * scale)
        indices.data[i * 6] = i * 4
        indices.data[i * 6 + 1] = i * 4 + 1
        indices.data[i * 6 + 2] = i * 4
        indices.data[i * 6 + 3] = i * 4 + 2
        indices.data[i * 6 + 4] = i * 4
        indices.data[i * 6 + 5] = i * 4 + 3
    return vectors, indices
