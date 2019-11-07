from ... math cimport (
    Matrix4,
    Vector3
)

from ... data_structures cimport (
    Matrix4x4List,
    FloatList,
    VirtualVector3DList
)

ctypedef void (*TranslationFunction)(Matrix4 *m, Vector3 *v)

cpdef translateMatrixList(Matrix4x4List matrices, str type,
                          VirtualVector3DList translations, FloatList influences)

cdef TranslationFunction getTranslationFunction(str type) except *
