from cpython.mem cimport PyMem_Malloc, PyMem_Free
from .. math cimport (setScaleMatrix, setRotationMatrix, setTranslationMatrix,
                      multMatrix4, multMatrix3Parts, transformVec3AsDirection)

cdef void allocateMatrixTransformer(
            TransformMatrixFunction* outFunction, void** outSettings,
            Vector3* translation, bint localAxis,
            Euler3* rotation, bint localRotationAxis, bint localRotationPivot,
            Vector3* scale, bint localScaleAxis, bint localScalePivot):

    cdef GenericSettings* settings = <GenericSettings*>PyMem_Malloc(sizeof(GenericSettings))

    settings.translate = selectTranslationFunction(translation, localAxis)
    settings.rotate = selectRotationFunction(rotation, localRotationAxis, localRotationPivot)
    settings.scale = selectScaleFunction(scale, localScaleAxis, localScalePivot)

    outFunction[0] = selectTransformFunction(translation, rotation, scale)
    outSettings[0] = settings

cdef freeMatrixTransformer(TransformMatrixFunction function, void* settings):
    PyMem_Free(settings)


ctypedef void (*TranslationFunction)(Matrix4* target, Matrix4* source, Matrix4* original, Vector3* translation)
ctypedef void (*RotationFunction)(Matrix4* target, Matrix4* source, Euler3* rotation)
ctypedef void (*ScaleFunction)(Matrix4* target, Matrix4* source, Vector3* scale)

cdef struct GenericSettings:
    TranslationFunction translate
    RotationFunction rotate
    ScaleFunction scale


# Transform Functions
#############################################################

cdef TransformMatrixFunction selectTransformFunction(
            Vector3* t, Euler3* r, Vector3* s):
    cdef:
        bint useTranslation = not (t.x == t.y == t.z == 0)
        bint useRotation = not (r.x == r.y == r.z == 0)
        bint useScale = not (s.x == s.y == s.z == 1)

    if useTranslation:
        if useRotation:
            if useScale: return transformMatrix_TranslateRotateScale
            else: return transformMatrix_TranslateRotate
        else:
            if useScale: return transformMatrix_TranslateScale
            else: return transformMatrix_Translate
    else:
        if useRotation:
            if useScale: return transformMatrix_RotateScale
            else: return transformMatrix_Rotate
        else:
            if useScale: return transformMatrix_Scale
            else: return transformMatrix_None

cdef void transformMatrix_TranslateRotateScale(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef:
        GenericSettings* _settings = <GenericSettings*>settings
        Matrix4 afterScale, afterRotation
    _settings.scale(&afterScale, source, scale)
    _settings.rotate(&afterRotation, &afterScale, rotation)
    _settings.translate(target, &afterRotation, source, translation)

cdef void transformMatrix_TranslateRotate(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef:
        GenericSettings* _settings = <GenericSettings*>settings
        Matrix4 afterRotation
    _settings.rotate(&afterRotation, source, rotation)
    _settings.translate(target, &afterRotation, source, translation)

cdef void transformMatrix_TranslateScale(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef:
        GenericSettings* _settings = <GenericSettings*>settings
        Matrix4 afterScale
    _settings.scale(&afterScale, source, scale)
    _settings.translate(target, &afterScale, source, translation)

cdef void transformMatrix_RotateScale(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef:
        GenericSettings* _settings = <GenericSettings*>settings
        Matrix4 afterScale, afterRotation
    _settings.scale(&afterScale, source, scale)
    _settings.rotate(target, &afterScale, rotation)

cdef void transformMatrix_Scale(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef GenericSettings* _settings = <GenericSettings*>settings
    _settings.scale(target, source, scale)

cdef void transformMatrix_Rotate(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef GenericSettings* _settings = <GenericSettings*>settings
    _settings.rotate(target, source, rotation)

cdef void transformMatrix_Translate(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef GenericSettings* _settings = <GenericSettings*>settings
    _settings.translate(target, source, source, translation)

cdef void transformMatrix_None(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    target[0] = source[0]


# Scale Functions
#############################################################

cdef ScaleFunction selectScaleFunction(Vector3* scale, bint localAxis, bint localPivot):
    if localAxis:
        if localPivot: return scale_LocalAxis_LocalPivot
        else: return scale_LocalAxis_GlobalPivot
    else:
        if localPivot: return scale_GlobalAxis_LocalPivot
        else: return scale_GlobalAxis_GlobalPivot

cdef void scale_LocalAxis_LocalPivot(Matrix4* target, Matrix4* source, Vector3* scale):
    cdef Matrix4 scaleMatrix
    setScaleMatrix(&scaleMatrix, scale)
    multMatrix3Parts(target, source, &scaleMatrix, keepFirst = True)

cdef void scale_LocalAxis_GlobalPivot(Matrix4* target, Matrix4* source, Vector3* scale):
    cdef Matrix4 scaleMatrix
    setScaleMatrix(&scaleMatrix, scale)
    multMatrix4(target, source, &scaleMatrix)

cdef void scale_GlobalAxis_LocalPivot(Matrix4* target, Matrix4* source, Vector3* scale):
    cdef Matrix4 scaleMatrix
    setScaleMatrix(&scaleMatrix, scale)
    multMatrix3Parts(target, &scaleMatrix, source, keepFirst = False)

cdef void scale_GlobalAxis_GlobalPivot(Matrix4* target, Matrix4* source, Vector3* scale):
    cdef Matrix4 scaleMatrix
    setScaleMatrix(&scaleMatrix, scale)
    multMatrix4(target, &scaleMatrix, source)


# Rotation Functions
#############################################################

cdef RotationFunction selectRotationFunction(Euler3* rotation, bint localAxis, bint localPivot):
    if localAxis:
        if localPivot: return rotate_LocalAxis_LocalPivot
        else: return rotate_LocalAxis_GlobalPivot
    else:
        if localPivot: return rotate_GlobalAxis_LocalPivot
        else: return rotate_GlobalAxis_GlobalPivot

cdef void rotate_LocalAxis_LocalPivot(Matrix4* target, Matrix4* source, Euler3* rotation):
    cdef Matrix4 rotationMatrix
    setRotationMatrix(&rotationMatrix, rotation)
    multMatrix3Parts(target, source, &rotationMatrix, keepFirst = True)

cdef void rotate_LocalAxis_GlobalPivot(Matrix4* target, Matrix4* source, Euler3* rotation):
    cdef Matrix4 rotationMatrix
    setRotationMatrix(&rotationMatrix, rotation)
    multMatrix4(target, source, &rotationMatrix)

cdef void rotate_GlobalAxis_LocalPivot(Matrix4* target, Matrix4* source, Euler3* rotation):
    cdef Matrix4 rotationMatrix
    setRotationMatrix(&rotationMatrix, rotation)
    multMatrix3Parts(target, &rotationMatrix, source, keepFirst = False)

cdef void rotate_GlobalAxis_GlobalPivot(Matrix4* target, Matrix4* source, Euler3* rotation):
    cdef Matrix4 rotationMatrix
    setRotationMatrix(&rotationMatrix, rotation)
    multMatrix4(target, &rotationMatrix, source)


# Translation Functions
#############################################################

cdef TranslationFunction selectTranslationFunction(Vector3* translation, bint localAxis):
    if localAxis: return translate_LocalAxis
    else: return translate_GlobalAxis

cdef void translate_LocalAxis(Matrix4* target, Matrix4* source, Matrix4* original, Vector3* translation):
    cdef Vector3 realOffset
    transformVec3AsDirection(&realOffset, translation, original)
    target[0] = source[0]
    target.a14 += realOffset.x
    target.a24 += realOffset.y
    target.a34 += realOffset.z

cdef void translate_GlobalAxis(Matrix4* target, Matrix4* source, Matrix4* original, Vector3* translation):
    target[0] = source[0]
    target.a14 += translation.x
    target.a24 += translation.y
    target.a34 += translation.z
