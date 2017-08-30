from ... math.vector cimport Vector3
from .. lists.base_lists cimport FloatList, Vector3DList

cdef class Spline:
    cdef:
        public bint cyclic
        readonly str type
        FloatList uniformParameters

    # Generic
    #############################################

    cpdef void markChanged(self)
    cpdef bint isEvaluable(self)


    # Uniform Conversion
    #############################################

    cdef checkUniformConverter(self)
    cpdef ensureUniformConverter(self, long resolution)
    cdef _updateUniformParameters(self, long totalResolution)

    cdef float toUniformParameter_LowLevel(self, float parameter)


    # Evaluate Single Parameter
    #############################################

    cdef void evaluatePoint_LowLevel(self, float t, Vector3 *result)
    cdef void evaluateTangent_LowLevel(self, float t, Vector3 *result)
    cdef float evaluateRadius_LowLevel(self, float t)


    # Projection
    #############################################

    cdef float project_LowLevel(self, Vector3 *point)
    cdef void projectExtended_LowLevel(self, Vector3 *point,
        Vector3 *resultPoint, Vector3 *resultTangent)


    # Trimming
    #############################################

    cdef Spline getTrimmedCopy_LowLevel(self, float start, float end)
