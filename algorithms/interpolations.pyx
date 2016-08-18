from .. data_structures cimport InterpolationBase

cdef class LinearInterpolation(InterpolationBase):
    cdef float evaluate(self, float x):
        return x

cdef class PowerInterpolation(InterpolationBase):
    cdef:
        int exponent

    def __cinit__(self, int exponent):
        self.exponent = max(exponent, 1)

    cdef float evaluate(self, float x):
        return x ** self.exponent
