from .. math cimport Vector3, Euler3, Matrix4, Matrix3

ctypedef void (*TransformMatrixFunction)(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale)

cdef void allocateMatrixTransformer(
            TransformMatrixFunction* outFunction, void** outSettings,
            Vector3* translation, bint localAxis,
            Euler3* rotation, bint localAxis, bint localPivot,
            Vector3* scale, bint localAxis, bint localPivot)

cdef freeMatrixTransformer(TransformMatrixFunction function, void* settings)
