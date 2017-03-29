from ... data_structures cimport (Vector3DList, EulerList, Matrix4x4List,
                                  CDefaultList, FloatList, DoubleList)

from ... math cimport (Vector3, Euler3, Matrix4,
                       setTranslationRotationScaleMatrix,
                       setRotationXMatrix, setRotationYMatrix, setRotationZMatrix,
                       setRotationMatrix)
from ... math import matrix4x4ListToEulerList

from libc.math cimport sqrt

def composeMatrices(translations, rotations, scales):
    cdef:
        CDefaultList _translations = CDefaultList(Vector3DList, translations, (0, 0, 0))
        CDefaultList _rotations = CDefaultList(EulerList, rotations, (0, 0, 0))
        CDefaultList _scales = CDefaultList(Vector3DList, scales, (1, 1, 1))

        long length = CDefaultList.getMaxLength(_translations, _rotations, _scales)
        Matrix4x4List matrices = Matrix4x4List(length = length)
        long i

    for i in range(matrices.length):
        setTranslationRotationScaleMatrix(matrices.data + i,
            <Vector3*>_translations.get(i),
            <Euler3*>_rotations.get(i),
            <Vector3*>_scales.get(i))

    return matrices

def extractMatrixTranslations(Matrix4x4List matrices):
    cdef Vector3DList translations = Vector3DList(length = len(matrices))
    cdef Matrix4 *_matrices = matrices.data
    cdef Vector3 *_translations = translations.data
    cdef Py_ssize_t i

    for i in range(len(translations)):
        _translations[i].x = _matrices[i].a14
        _translations[i].y = _matrices[i].a24
        _translations[i].z = _matrices[i].a34

    return translations

def extractMatrixRotations(Matrix4x4List matrices):
    return matrix4x4ListToEulerList(matrices)

def extractMatrixScales(Matrix4x4List matrices):
    cdef Vector3DList scales = Vector3DList(length = len(matrices))
    cdef Py_ssize_t i

    for i in range(len(scales)):
        scaleFromMatrix(scales.data + i, matrices.data + i)

    return scales

cdef void scaleFromMatrix(Vector3 *scale, Matrix4 *matrix):
    scale.x = sqrt(matrix.a11 * matrix.a11 + matrix.a21 * matrix.a21 + matrix.a31 * matrix.a31)
    scale.y = sqrt(matrix.a12 * matrix.a12 + matrix.a22 * matrix.a22 + matrix.a32 * matrix.a32)
    scale.z = sqrt(matrix.a13 * matrix.a13 + matrix.a23 * matrix.a23 + matrix.a33 * matrix.a33)

def createAxisRotations(DoubleList angles, str axis):
    cdef Matrix4x4List matrices = Matrix4x4List(length = len(angles))
    cdef int i
    if axis == "X":
        for i in range(len(matrices)):
            setRotationXMatrix(matrices.data + i, angles.data[i])
    elif axis == "Y":
        for i in range(len(matrices)):
            setRotationYMatrix(matrices.data + i, angles.data[i])
    elif axis == "Z":
        for i in range(len(matrices)):
            setRotationZMatrix(matrices.data + i, angles.data[i])
    return matrices

def createRotationsFromEulers(EulerList rotations):
    cdef Matrix4x4List matrices = Matrix4x4List(length = len(rotations))
    cdef int i
    for i in range(len(matrices)):
        setRotationMatrix(matrices.data + i, rotations.data + i)
    return matrices
