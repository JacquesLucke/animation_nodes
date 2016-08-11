from ... math.ctypes cimport Vector3
from .. lists.base_lists cimport FloatList
from .. lists.complex_lists cimport Vector3DList

ctypedef void (*EvaluationFunction)(Spline, float, Vector3*)

cdef class Spline:
    cdef:
        public bint cyclic
        readonly str type
        FloatList uniformParameters

    cpdef Spline copy(self)
    cpdef void markChanged(self)
    cpdef bint isEvaluable(self)
    cpdef transform(self, matrix)

    cpdef ensureUniformConverter(self, long resolution)
    cdef updateUniformParameters(self, long resolution)
    cpdef toUniformParameter(self, float parameter)
    cdef float toUniformParameter_LowLevel(self, float parameter)

    cpdef double getLength(self, resolution = ?)

    cpdef getSamples(self, long amount, float start = ?, float end = ?)
    cpdef getTangentSamples(self, long amount, float start = ?, float end = ?)
    cpdef getUniformSamples(self, long amount, float start = ?, float end = ?)
    cpdef getUniformTangentSamples(self, long amount, float start = ?, float end = ?)

    cpdef evaluate(self, float parameter)
    cpdef evaluateTangent(self, float parameter)

    cdef void evaluate_LowLevel(self, float parameter, Vector3* result)
    cdef void evaluateTangent_LowLevel(self, float parameter, Vector3* result)
    cdef void evaluateUniform_LowLevel(self, float parameter, Vector3* result)
    cdef void evaluateUniformTangent_LowLevel(self, float parameter, Vector3* result)

    cdef sampleEvaluationFunction(self, EvaluationFunction evaluate,
                                        long amount, float start, float end)

    cdef void sampleEvaluationFunction_LowLevel(self, EvaluationFunction evaluate,
                                                long amount, float start, float end,
                                                Vector3* output)
