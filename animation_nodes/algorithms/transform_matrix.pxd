from .. data_structures cimport CListMock
from .. math cimport Vector3, Euler3, Matrix4, Matrix3

ctypedef void (*TransformMatrixFunction)(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale)

cdef void allocateMatrixTransformerFromSingleValues(
            TransformMatrixFunction* outFunction, void** outSettings,
            Vector3* translation, bint localTranslationAxis,
            Euler3* rotation, bint localRotationAxis, bint localRotationPivot,
            Vector3* scale, bint localScaleAxis, bint localScalePivot)

cdef void allocateMatrixTransformerFromCListMocks(
            TransformMatrixFunction* outFunction, void** outSettings,
            CListMock translations, bint localTranslationAxis,
            CListMock rotations, bint localRotationAxis, bint localRotationPivot,
            CListMock scales, bint localScaleAxis, bint localScalePivot)

cdef freeMatrixTransformer(TransformMatrixFunction function, void* settings)
