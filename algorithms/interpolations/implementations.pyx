from libc.math cimport pow
from ... data_structures cimport InterpolationBase

# Linear
#####################################################

cdef class Linear(InterpolationBase):
    cdef double evaluate(self, double x):
        return x


# Power
#####################################################

cdef class PowerIn(InterpolationBase):
    cdef int exponent

    def __cinit__(self, int exponent):
        self.exponent = max(exponent, 1)

    cdef double evaluate(self, double x):
        return pow(x, self.exponent)

cdef class PowerOut(InterpolationBase):
    cdef int exponent
    cdef int factor

    def __cinit__(self, int exponent):
        self.exponent = max(exponent, 1)
        self.factor = -1 if self.exponent % 2 == 0 else 1

    cdef double evaluate(self, double x):
        return pow(x - 1, self.exponent) * self.factor + 1

cdef class PowerInOut(InterpolationBase):
    cdef int exponent
    cdef double factor

    def __cinit__(self, int exponent):
        self.exponent = max(exponent, 1)
        self.factor = -0.5 if self.exponent % 2 == 0 else 0.5

    cdef double evaluate(self, double x):
        if x <= 0.5:
            return pow(x * 2, self.exponent) / 2
        else:
            return pow((x - 1) * 2, self.exponent) * self.factor + 1


# Exponential
#####################################################

cdef class ExponentialInterpolationBase(InterpolationBase):
    cdef:
        int exponent
        double base
        double minValue
        double scale

    def __cinit__(self, double base, int exponent):
        self.exponent = min(max(0, exponent), 70)
        self.base = max(0.0001, base) if base != 1 else 1.0001
        self.minValue = pow(self.base, -self.exponent)
        self.scale = 1 / (1 - self.minValue)

cdef class ExponentialIn(ExponentialInterpolationBase):
    cdef double evaluate(self, double x):
        return (pow(self.base, self.exponent * (x - 1)) - self.minValue) * self.scale

cdef class ExponentialOut(ExponentialInterpolationBase):
    cdef double evaluate(self, double x):
        return 1 - (pow(self.base, -self.exponent * x) - self.minValue) * self.scale

cdef class ExponentialInOut(ExponentialInterpolationBase):
    cdef double evaluate(self, double x):
        if x <= 0.5:
            return (pow(self.base, self.exponent * (x * 2 - 1)) - self.minValue) * self.scale / 2
        else:
            return (2 - (pow(self.base, -self.exponent * (x * 2 - 1)) - self.minValue) * self.scale) / 2
