from libc.math cimport pow
from ... data_structures cimport InterpolationBase

# Linear
#####################################################

cdef class Linear(InterpolationBase):
    cdef float evaluate(self, float x):
        return x


# Power
#####################################################

cdef class PowerIn(InterpolationBase):
    cdef int exponent

    def __cinit__(self, int exponent):
        self.exponent = max(exponent, 1)

    cdef float evaluate(self, float x):
        return pow(x, self.exponent)

cdef class PowerOut(InterpolationBase):
    cdef int exponent
    cdef int factor

    def __cinit__(self, int exponent):
        self.exponent = max(exponent, 1)
        self.factor = -1 if self.exponent % 2 == 0 else 1

    cdef float evaluate(self, float x):
        return pow(x - 1, self.exponent) * self.factor + 1

cdef class PowerInOut(InterpolationBase):
    cdef int exponent
    cdef float factor

    def __cinit__(self, int exponent):
        self.exponent = max(exponent, 1)
        self.factor = -0.5 if self.exponent % 2 == 0 else 0.5

    cdef float evaluate(self, float x):
        if x <= 0.5:
            return pow(x * 2, self.exponent) / 2
        else:
            return pow((x - 1) * 2, self.exponent) * self.factor + 1
