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
