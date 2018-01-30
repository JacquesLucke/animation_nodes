from ... math cimport (
    Matrix4,
    Vector3
)

from ... data_structures cimport (
    Matrix4x4List,
    FloatList,
    VirtualVector3DList
)

ctypedef void (*ScaleFunction)(Matrix4 *m, Vector3 *v)

cpdef scaleMatrixList(Matrix4x4List matrices, str type,
                      VirtualVector3DList scales, FloatList influences)

cdef ScaleFunction getScaleFunction(str type) except *
