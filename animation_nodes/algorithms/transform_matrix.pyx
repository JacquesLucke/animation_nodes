from cpython.mem cimport PyMem_Malloc, PyMem_Free
from .. math cimport (setScaleMatrix, setRotationMatrix, setTranslationMatrix,
              multMatrix4, multMatrix3Parts, transformVec3AsDirection,
              setRotationXMatrix, setRotationYMatrix, setRotationZMatrix,
              mult3xMatrix_Reversed, convertMatrix3ToMatrix4, setIdentityMatrix)

cdef struct MatrixTransformerSettings:
    # Location
    bint useTranslation
    bint localTranslationAxis
    # Rotation
    bint useRotationX, useRotationY, useRotationZ
    bint onlyRotationOrderXYZ
    bint localRotationAxis, localRotationPivot
    # Scale
    bint useScale
    bint localScaleAxis, localScalePivot

cdef void allocateMatrixTransformerFromSingleValues(
            TransformMatrixFunction* outFunction, void** outSettings,
            Vector3* translation, bint localTranslationAxis,
            Euler3* rotation, bint localRotationAxis, bint localRotationPivot,
            Vector3* scale, bint localScaleAxis, bint localScalePivot):
    cdef MatrixTransformerSettings s

    s.useTranslation = not (translation.x == translation.y == translation.z == 0)
    s.localTranslationAxis = localTranslationAxis

    s.useRotationX = rotation.x != 0
    s.useRotationY = rotation.y != 0
    s.useRotationZ = rotation.z != 0
    s.onlyRotationOrderXYZ = rotation.order == 0
    s.localRotationAxis = localRotationAxis
    s.localRotationPivot = localRotationPivot

    s.useScale = not (scale.x == scale.y == scale.z == 1)
    s.localScaleAxis = localScaleAxis
    s.localScalePivot = localScalePivot

    allocateMatrixTransformer(outFunction, outSettings, &s)

cdef void allocateMatrixTransformer(
            TransformMatrixFunction* outFunction, void** outSettings,
            MatrixTransformerSettings* s):

    cdef GenericSettings* settings = <GenericSettings*>PyMem_Malloc(sizeof(GenericSettings))

    settings.translate = selectTranslationFunction(s)
    settings.rotate = selectRotationFunction(s)
    settings.scale = selectScaleFunction(s)
    settings.setRotation = selectSetRotationFunction(s)

    outFunction[0] = selectTransformFunction(s)
    outSettings[0] = settings

cdef freeMatrixTransformer(TransformMatrixFunction function, void* settings):
    PyMem_Free(settings)


ctypedef void (*SetRotationFunction)(Matrix4* target, Euler3* rotation)
ctypedef void (*TranslationFunction)(Matrix4* target, Matrix4* source, Matrix4* original, Vector3* translation)
ctypedef void (*RotationFunction)(Matrix4* target, Matrix4* source, Euler3* rotation, SetRotationFunction setRotation)
ctypedef void (*ScaleFunction)(Matrix4* target, Matrix4* source, Vector3* scale)

cdef struct GenericSettings:
    TranslationFunction translate
    RotationFunction rotate
    ScaleFunction scale
    SetRotationFunction setRotation


# Transform Functions
#############################################################

cdef TransformMatrixFunction selectTransformFunction(
            MatrixTransformerSettings* s):
    cdef:
        bint _useTranslation = s.useTranslation
        bint _useRotation = s.useRotationX or s.useRotationY or s.useRotationZ
        bint _useScale = s.useScale

    if _useTranslation:
        if _useRotation:
            if _useScale: return transformMatrix_TranslateRotateScale
            else: return transformMatrix_TranslateRotate
        else:
            if _useScale: return transformMatrix_TranslateScale
            else: return transformMatrix_Translate
    else:
        if _useRotation:
            if _useScale: return transformMatrix_RotateScale
            else: return transformMatrix_Rotate
        else:
            if _useScale: return transformMatrix_Scale
            else: return transformMatrix_None

cdef void transformMatrix_TranslateRotateScale(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef:
        GenericSettings* _settings = <GenericSettings*>settings
        Matrix4 afterScale, afterRotation
    _settings.scale(&afterScale, source, scale)
    _settings.rotate(&afterRotation, &afterScale, rotation, _settings.setRotation)
    _settings.translate(target, &afterRotation, source, translation)

cdef void transformMatrix_TranslateRotate(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef:
        GenericSettings* _settings = <GenericSettings*>settings
        Matrix4 afterRotation
    _settings.rotate(&afterRotation, source, rotation, _settings.setRotation)
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
    _settings.rotate(target, &afterScale, rotation, _settings.setRotation)

cdef void transformMatrix_Scale(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef GenericSettings* _settings = <GenericSettings*>settings
    _settings.scale(target, source, scale)

cdef void transformMatrix_Rotate(
            void* settings, Matrix4* target, Matrix4* source,
            Vector3* translation, Euler3* rotation, Vector3* scale):
    cdef GenericSettings* _settings = <GenericSettings*>settings
    _settings.rotate(target, source, rotation, _settings.setRotation)

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

cdef ScaleFunction selectScaleFunction(MatrixTransformerSettings* s):
    if s.localScaleAxis:
        if s.localScalePivot: return scale_LocalAxis_LocalPivot
        else: return scale_LocalAxis_GlobalPivot
    else:
        if s.localScalePivot: return scale_GlobalAxis_LocalPivot
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

cdef RotationFunction selectRotationFunction(MatrixTransformerSettings* s):
    if s.localRotationAxis:
        if s.localRotationPivot: return rotate_LocalAxis_LocalPivot
        else: return rotate_LocalAxis_GlobalPivot
    else:
        if s.localRotationPivot: return rotate_GlobalAxis_LocalPivot
        else: return rotate_GlobalAxis_GlobalPivot

cdef void rotate_LocalAxis_LocalPivot(Matrix4* target, Matrix4* source, Euler3* rotation, SetRotationFunction setRotation):
    cdef Matrix4 rotationMatrix
    setRotation(&rotationMatrix, rotation)
    multMatrix3Parts(target, source, &rotationMatrix, keepFirst = True)

cdef void rotate_LocalAxis_GlobalPivot(Matrix4* target, Matrix4* source, Euler3* rotation, SetRotationFunction setRotation):
    cdef Matrix4 rotationMatrix
    setRotation(&rotationMatrix, rotation)
    multMatrix4(target, source, &rotationMatrix)

cdef void rotate_GlobalAxis_LocalPivot(Matrix4* target, Matrix4* source, Euler3* rotation, SetRotationFunction setRotation):
    cdef Matrix4 rotationMatrix
    setRotation(&rotationMatrix, rotation)
    multMatrix3Parts(target, &rotationMatrix, source, keepFirst = False)

cdef void rotate_GlobalAxis_GlobalPivot(Matrix4* target, Matrix4* source, Euler3* rotation, SetRotationFunction setRotation):
    cdef Matrix4 rotationMatrix
    setRotation(&rotationMatrix, rotation)
    multMatrix4(target, &rotationMatrix, source)


# Translation Functions
#############################################################

cdef TranslationFunction selectTranslationFunction(MatrixTransformerSettings* s):
    if s.localTranslationAxis: return translate_LocalAxis
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


# Set Rotation Functions
#############################################################

cdef SetRotationFunction selectSetRotationFunction(MatrixTransformerSettings* s):
    cdef:
        bint useX = s.useRotationX
        bint useY = s.useRotationY
        bint useZ = s.useRotationZ

    if not s.onlyRotationOrderXYZ:
        return setRotationMatrix[Matrix4]

    if useX:
        if useY:
            if useZ: return setRotationMatrix_XYZ
            else: return setRotationMatrix_XY
        else:
            if useZ: return setRotationMatrix_XZ
            else: return setRotationMatrix_X
    else:
        if useY:
            if useZ: return setRotationMatrix_YZ
            else: return setRotationMatrix_Y
        else:
            if useZ: return setRotationMatrix_Z
            else: return setRotationMatrix_None

cdef void setRotationMatrix_XYZ(Matrix4* m, Euler3* e):
    cdef Matrix3 xMat, yMat, zMat, rotation
    setRotationXMatrix(&xMat, e.x)
    setRotationYMatrix(&yMat, e.y)
    setRotationZMatrix(&zMat, e.z)
    mult3xMatrix_Reversed(&rotation, &xMat, &yMat, &zMat)
    convertMatrix3ToMatrix4(m, &rotation)

cdef void setRotationMatrix_XY(Matrix4* m, Euler3* e):
    cdef Matrix4 xMat, yMat
    setRotationXMatrix(&xMat, e.x)
    setRotationYMatrix(&yMat, e.y)
    multMatrix4(m, &yMat, &xMat)

cdef void setRotationMatrix_XZ(Matrix4* m, Euler3* e):
    cdef Matrix4 xMat, zMat
    setRotationXMatrix(&xMat, e.x)
    setRotationZMatrix(&zMat, e.z)
    multMatrix4(m, &zMat, &xMat)

cdef void setRotationMatrix_YZ(Matrix4* m, Euler3* e):
    cdef Matrix4 yMat, zMat
    setRotationYMatrix(&yMat, e.y)
    setRotationZMatrix(&zMat, e.z)
    multMatrix4(m, &zMat, &yMat)

cdef void setRotationMatrix_X(Matrix4* m, Euler3* e):
    setRotationXMatrix(m, e.x)

cdef void setRotationMatrix_Y(Matrix4* m, Euler3* e):
    setRotationYMatrix(m, e.y)

cdef void setRotationMatrix_Z(Matrix4* m, Euler3* e):
    setRotationZMatrix(m, e.z)

cdef void setRotationMatrix_None(Matrix4* m, Euler3* e):
    setIdentityMatrix(m)
