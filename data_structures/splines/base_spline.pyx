cdef class Spline:
    pass

    cpdef Spline copy(self):
        raise NotImplementedError()

    cpdef transform(self, matrix):
        raise NotImplementedError()

    cpdef double getLength(self, resolution = 0):
        raise NotImplementedError()

    cpdef bint isEvaluable(self):
        raise NotImplementedError()

    cpdef evaluate(self, float t):
        raise NotImplementedError()

    cpdef evaluateTangent(self, float t):
        raise NotImplementedError()

    cpdef void update(self):
        raise NotImplementedError()
