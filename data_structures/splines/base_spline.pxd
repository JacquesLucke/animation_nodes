from ... math.ctypes cimport Vector3

cdef class Spline:
    cdef:
        public bint cyclic
        readonly str type

    cpdef Spline copy(self)
    cpdef transform(self, matrix)
    cpdef double getLength(self, resolution = ?)
    cpdef bint isEvaluable(self)
    cpdef evaluate(self, float t)
    cpdef evaluateTangent(self, float t)
    cpdef void update(self)

    cdef void evaluate_LowLevel(self, float t, Vector3* result)
    cdef void evaluateTangent_LowLevel(self, float t, Vector3* result)

    cpdef getSamples(self, long amount, float start = ?, float end = ?)
