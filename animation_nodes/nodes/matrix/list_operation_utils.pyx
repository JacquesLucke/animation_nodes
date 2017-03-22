from ... data_structures cimport (Vector3DList, EulerList, Matrix4x4List,
                                  CListMock)

from ... math cimport setTranslationRotationScaleMatrix, Vector3, Euler3

def composeMatrices(translations, rotations, scales):
    cdef:
        CListMock _translations = CListMock(Vector3DList, translations, (0, 0, 0))
        CListMock _rotations = CListMock(EulerList, rotations, (0, 0, 0))
        CListMock _scales = CListMock(Vector3DList, scales, (1, 1, 1))

        long length = CListMock.getMaxLength(_translations, _rotations, _scales)
        Matrix4x4List matrices = Matrix4x4List(length = length)
        long i

    for i in range(matrices.length):
        setTranslationRotationScaleMatrix(matrices.data + i,
            <Vector3*>_translations.get(i),
            <Euler3*>_rotations.get(i),
            <Vector3*>_scales.get(i))

    return matrices
