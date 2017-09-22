from ... data_structures cimport (
    DoubleList, FloatList,
    Vector3DList, EulerList, Matrix4x4List,
    VirtualVector3DList, VirtualEulerList, VirtualFloatList,
    Action, ActionEvaluator, PathIndexActionChannel,
    BoundedAction, BoundedActionEvaluator
)

from ... math cimport (
    Vector3, Euler3, Matrix4, toMatrix4,
    multMatrix4, toPyMatrix4,
    setTranslationRotationScaleMatrix,
    setRotationXMatrix, setRotationYMatrix, setRotationZMatrix,
    setRotationMatrix, setTranslationMatrix, setIdentityMatrix,
    setScaleMatrix,
    setMatrixTranslation,
    transposeMatrix_Inplace)

from ... math import matrix4x4ListToEulerList

from libc.math cimport sqrt
from libc.math cimport M_PI as PI


# Compose/Create Matrix
########################################

def composeMatrices(Py_ssize_t amount, VirtualVector3DList translations,
                    VirtualEulerList rotations, VirtualVector3DList scales):
    cdef Matrix4x4List matrices = Matrix4x4List(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        setTranslationRotationScaleMatrix(matrices.data + i,
            translations.get(i), rotations.get(i), scales.get(i))

    return matrices

def createAxisRotations(DoubleList angles, str axis, bint useDegree):
    cdef Matrix4x4List matrices = Matrix4x4List(length = angles.length)
    cdef float factor = <float>(PI / 180 if useDegree else 1)

    cdef Py_ssize_t i
    if axis == "X":
        for i in range(matrices.length):
            setRotationXMatrix(matrices.data + i, <float>angles.data[i] * factor)
    elif axis == "Y":
        for i in range(matrices.length):
            setRotationYMatrix(matrices.data + i, <float>angles.data[i] * factor)
    elif axis == "Z":
        for i in range(matrices.length):
            setRotationZMatrix(matrices.data + i, <float>angles.data[i] * factor)
    return matrices

def rotationsFromVirtualEulers(Py_ssize_t amount, VirtualEulerList rotations):
    cdef Matrix4x4List matrices = Matrix4x4List(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        setRotationMatrix(matrices.data + i, rotations.get(i))
    return matrices

def scalesFromVirtualVectors(Py_ssize_t amount, VirtualVector3DList scales):
    cdef Matrix4x4List matrices = Matrix4x4List(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        setScaleMatrix(matrices.data + i, scales.get(i))
    return matrices

def scale3x3Parts(Matrix4x4List matrices, VirtualVector3DList scales):
    cdef Py_ssize_t i
    cdef Matrix4 *m
    cdef Vector3 *s
    for i in range(matrices.length):
        m = matrices.data + i
        s = scales.get(i)
        m.a11 *= s.x; m.a12 *= s.y; m.a13 *= s.z
        m.a21 *= s.x; m.a22 *= s.y; m.a23 *= s.z
        m.a31 *= s.x; m.a32 *= s.y; m.a33 *= s.z

def setLocations(Matrix4x4List matrices, VirtualVector3DList locations):
    cdef Py_ssize_t i
    for i in range(matrices.length):
        setMatrixTranslation(matrices.data + i, locations.get(i))

def createRotationsFromEulers(EulerList rotations):
    cdef Matrix4x4List matrices = Matrix4x4List(length = len(rotations))
    cdef int i
    for i in range(len(matrices)):
        setRotationMatrix(matrices.data + i, rotations.data + i)
    return matrices

def createTranslationMatrices(Vector3DList vectors):
    cdef Matrix4x4List matrices = Matrix4x4List(length = vectors.length)
    cdef Py_ssize_t i
    for i in range(vectors.length):
        setTranslationMatrix(matrices.data + i, vectors.data + i)
    return matrices


# Extract Matrix Information
################################################

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

cdef void scaleFromMatrix(Vector3 *scale, Matrix4 *m):
    scale.x = <float>sqrt(m.a11 * m.a11 + m.a21 * m.a21 + m.a31 * m.a31)
    scale.y = <float>sqrt(m.a12 * m.a12 + m.a22 * m.a22 + m.a32 * m.a32)
    scale.z = <float>sqrt(m.a13 * m.a13 + m.a23 * m.a23 + m.a33 * m.a33)


# Replicate Matrix
###############################################

def replicateMatrixAtMatrices(matrix, Matrix4x4List transformations):
    cdef Matrix4 _matrix = toMatrix4(matrix)
    cdef Matrix4x4List result = Matrix4x4List(length = len(transformations))
    cdef Py_ssize_t i
    for i in range(len(result)):
        multMatrix4(result.data + i, transformations.data + i, &_matrix)
    return result

def replicateMatrixAtVectors(matrix, Vector3DList translations):
    cdef Matrix4 _matrix = toMatrix4(matrix)
    cdef Matrix4x4List result = Matrix4x4List(length = len(translations))
    cdef Py_ssize_t i
    for i in range(len(result)):
        result.data[i] = _matrix
        result.data[i].a14 += translations.data[i].x
        result.data[i].a24 += translations.data[i].y
        result.data[i].a34 += translations.data[i].z
    return result

def replicateMatricesAtMatrices(Matrix4x4List matrices, Matrix4x4List transformations):
    cdef Matrix4x4List result = Matrix4x4List(length = len(matrices) * len(transformations))
    cdef Py_ssize_t i, j
    for i in range(len(transformations)):
        for j in range(matrices.length):
            multMatrix4(result.data + i * matrices.length + j,
                        transformations.data + i,
                        matrices.data + j)
    return result

def replicateMatricesAtVectors(Matrix4x4List matrices, Vector3DList translations):
    cdef Matrix4x4List result = Matrix4x4List(length = len(matrices) * len(translations))
    cdef Py_ssize_t i, j, index
    for i in range(len(translations)):
        for j in range(matrices.length):
            index = i * matrices.length + j
            result.data[index] = matrices.data[j]
            result.data[index].a14 += translations.data[i].x
            result.data[index].a24 += translations.data[i].y
            result.data[index].a34 += translations.data[i].z
    return result


# Multiply Matrices
##########################################

def vectorizedMatrixMultiplication(matricesA, matricesB):
    cdef bint isListA = isinstance(matricesA, Matrix4x4List)
    cdef bint isListB = isinstance(matricesB, Matrix4x4List)
    if isListA and isListB:
        return multiplyMatrixLists(matricesA, matricesB)
    elif isListA:
        return multiplyMatrixWithList(matricesA, matricesB, "RIGHT")
    elif isListB:
        return multiplyMatrixWithList(matricesB, matricesA, "LEFT")
    else:
        return matricesA * matricesB

def multiplyMatrixWithList(Matrix4x4List matrices, _transformation, str type):
    cdef Matrix4 transformation = toMatrix4(_transformation)
    cdef Matrix4x4List outMatrices = Matrix4x4List(length = len(matrices))
    cdef Py_ssize_t i
    if type == "LEFT":
        for i in range(len(outMatrices)):
            multMatrix4(outMatrices.data + i, &transformation, matrices.data + i)
    elif type == "RIGHT":
        for i in range(len(outMatrices)):
            multMatrix4(outMatrices.data + i, matrices.data + i, &transformation)
    else:
        raise Exception("type has to be 'LEFT' or 'RIGHT'")
    return outMatrices

def multiplyMatrixLists(Matrix4x4List listA, Matrix4x4List listB):
    assert listA.length == listB.length

    cdef Matrix4x4List outMatrices = Matrix4x4List(length = len(listA))
    cdef Py_ssize_t i
    for i in range(len(listA)):
        multMatrix4(outMatrices.data + i, listA.data + i, listB.data + i)
    return outMatrices


# Various
###########################################

def reduceMatrixList(Matrix4x4List matrices, bint reversed):
    cdef:
        Py_ssize_t i
        Matrix4 tmp, target
        Py_ssize_t amount = len(matrices)

    if amount == 0:
        setIdentityMatrix(&target)
    elif amount == 1:
        target = matrices.data[0]
    else:
        if reversed:
            tmp = matrices.data[amount - 1]
            for i in range(amount - 2, -1, -1):
                multMatrix4(&target, &tmp, matrices.data + i)
                tmp = target
        else:
            tmp = matrices.data[0]
            for i in range(1, amount):
                multMatrix4(&target, &tmp, matrices.data + i)
                tmp = target

    return toPyMatrix4(&target)


cdef list transformationChannels = PathIndexActionChannel.forArrays(
    ["location", "rotation_euler", "scale"], 3)
cdef FloatList transformationDefaults = FloatList.fromValues(
    [0, 0, 0,  0, 0, 0,  1, 1, 1])

def evaluateTransformationAction(Action action, float frame, Py_ssize_t amount):
    cdef ActionEvaluator evaluator = action.getEvaluator(
        transformationChannels, transformationDefaults)

    cdef FloatList results = FloatList(length = len(transformationChannels))
    cdef float *_results = results.data

    cdef Vector3DList locations = Vector3DList(length = amount)
    cdef EulerList rotations = EulerList(length = amount)
    cdef Vector3DList scales = Vector3DList(length = amount)

    cdef Py_ssize_t i
    for i in range(amount):
        evaluator.evaluate(frame, i, _results)
        locations.data[i] = Vector3(_results[0], _results[1], _results[2])
        rotations.data[i] = Euler3(_results[3], _results[4], _results[5], 0)
        scales.data[i] = Vector3(_results[6], _results[7], _results[8])

    return locations, rotations, scales

def evaluateBoundedTransformationAction(BoundedAction action, FloatList parameters):
    cdef BoundedActionEvaluator evaluator = action.getEvaluator(
        transformationChannels, transformationDefaults)

    cdef FloatList results = FloatList(length = len(transformationDefaults))
    cdef float *_results = results.data

    cdef Py_ssize_t amount = parameters.length
    cdef Vector3DList locations = Vector3DList(length = amount)
    cdef EulerList rotations = EulerList(length = amount)
    cdef Vector3DList scales = Vector3DList(length = amount)

    cdef Py_ssize_t i
    for i in range(amount):
        evaluator.evaluateBounded(parameters.data[i], i, _results)
        locations.data[i] = Vector3(_results[0], _results[1], _results[2])
        rotations.data[i] = Euler3(_results[3], _results[4], _results[5], 0)
        scales.data[i] = Vector3(_results[6], _results[7], _results[8])

    return locations, rotations, scales
