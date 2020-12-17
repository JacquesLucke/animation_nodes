from ... math.vector cimport Vector3
from ... math.matrix cimport Matrix4
from .. lists.base_lists cimport FloatList, Vector3DList, Matrix4x4List

cdef class Spline:
    cdef:
        public bint cyclic
        readonly str type
        FloatList uniformParameters

    # Generic
    #############################################

    cpdef void markChanged(self)
    cpdef bint isEvaluable(self)
    cdef checkEvaluability(self)


    # Uniform Conversion
    #############################################

    cdef checkUniformConverter(self)
    cpdef ensureUniformConverter(self, Py_ssize_t minResolution)
    cdef _updateUniformParameters(self, Py_ssize_t totalResolution)

    cdef float toUniformParameter_LowLevel(self, float parameter)


    # Normals
    #############################################

    cdef checkNormals(self)
    cpdef ensureNormals(self)

    cdef calcDistributedNormals_LowLevel(self, Py_ssize_t amount, Vector3 *result,
        float start = ?, float end = ?,
        str distributionType = ?)

    cdef calcDistributedTilts_LowLevel(self, Py_ssize_t amount, float *result,
        float start = ?, float end = ?,
        str distributionType = ?)


    # Evaluate Single Parameter
    #############################################

    cdef void evaluatePoint_LowLevel(self, float t, Vector3 *result)
    cdef void evaluateTangent_LowLevel(self, float t, Vector3 *result)
    cdef void evaluateNormal_LowLevel(self, float t, Vector3 *result)
    cdef void evaluateNormal_Approximated(self, float t, Vector3 *result)
    cdef float evaluateCurvature_LowLevel(self, float t)
    cdef float evaluateRadius_LowLevel(self, float t)
    cdef float evaluateTilt_LowLevel(self, float t)
    cdef void evaluateMatrix_LowLevel(self, float t, Matrix4 *result)


    # Evaluate Multiple Parameters
    #############################################

    cdef calcDistributedPoints_LowLevel(self, Py_ssize_t amount, Vector3 *result,
        float start = ?, float end = ?,
        str distributionType = ?)
    cdef calcDistributedTangents_LowLevel(self, Py_ssize_t amount, Vector3 *result,
        float start = ?, float end = ?,
        str distributionType = ?)
    cdef calcDistributedNormals_LowLevel(self, Py_ssize_t amount, Vector3 *result,
        float start = ?, float end = ?,
        str distributionType = ?)
    cdef calcDistributedCurvatures_LowLevel(self, Py_ssize_t amount, float *result,
        float start = ?, float end = ?,
        str distributionType = ?)
    cdef calcDistributedRadii_LowLevel(self, Py_ssize_t amount, float *result,
        float start = ?, float end = ?,
        str distributionType = ?)
    cdef calcDistributedTilts_LowLevel(self, Py_ssize_t amount, float *result,
        float start = ?, float end = ?,
        str distributionType = ?)
    cdef calcDistributedMatrices_LowLevel(self, Py_ssize_t amount, Matrix4 *result,
        float start = ?, float end = ?,
        str distributionType = ?)


    # Projection
    #############################################

    cdef float project_LowLevel(self, Vector3 *point)
    cdef void projectExtended_LowLevel(self, Vector3 *point,
        Vector3 *resultPoint, Vector3 *resultTangent)


    # Trimming
    #############################################

    cdef Spline getTrimmedCopy_LowLevel(self, float start, float end)
