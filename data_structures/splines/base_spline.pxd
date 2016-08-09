from ... math.ctypes cimport Vector3

ctypedef void (*EvaluationFunction)(Spline, float, Vector3*)

cdef class Spline:
    cdef:
        public bint cyclic
        readonly str type

    cpdef Spline copy(self)
    cpdef void update(self)
    cpdef bint isEvaluable(self)
    cpdef transform(self, matrix)

    cpdef double getLength(self, resolution = ?)

    cpdef getSamples(self, long amount, float start = ?, float end = ?)

    cpdef evaluate(self, float t)
    cpdef evaluateTangent(self, float t)

    cdef void evaluate_LowLevel(self, float t, Vector3* result)
    cdef void evaluateTangent_LowLevel(self, float t, Vector3* result)

    cdef sampleEvaluationFunction(self, EvaluationFunction evaluate,
                                        long amount, float start, float end)

    cdef void sampleEvaluationFunction_LowLevel(self, EvaluationFunction evaluate,
                                                long amount, float start, float end,
                                                Vector3* output)
