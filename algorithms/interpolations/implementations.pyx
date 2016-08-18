from libc.math cimport M_PI as PI
from libc.math cimport pow, sqrt, sin
from ... data_structures cimport InterpolationBase, DoubleList

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


# Circular
#####################################################

cdef class CircularIn(InterpolationBase):
    cdef double evaluate(self, double x):
        return 1 - sqrt(1 - x * x)

cdef class CircularOut(InterpolationBase):
    cdef double evaluate(self, double x):
        x -= 1
        return sqrt(1 - x * x)

cdef class CircularInOut(InterpolationBase):
    cdef double evaluate(self, double x):
        if x <= 0.5:
            x *= 2
            return (1 - sqrt(1 - x * x)) / 2
        else:
            x = (x - 1) * 2
            return (sqrt(1 - x * x) + 1) / 2

# Elastic
#####################################################

cdef class ElasticInterpolationBase(InterpolationBase):
    cdef:
        int factor
        double bounceFactor, base, exponent

    def __cinit__(self, int bounces, double base, double exponent):
        bounces = max(0, bounces)
        self.factor = -1 if bounces % 2 == 0 else 1
        self.base = max(0, base)
        self.bounceFactor = -(bounces + 0.5) * PI
        self.exponent = exponent

cdef class ElasticIn(ElasticInterpolationBase):
    cdef double evaluate(self, double x):
        return pow(self.base, self.exponent * (x - 1)) * sin(x * self.bounceFactor) * self.factor

cdef class ElasticOut(ElasticInterpolationBase):
    cdef double evaluate(self, double x):
        x = 1 - x
        return 1 - pow(self.base, self.exponent * (x - 1)) * sin(x * self.bounceFactor) * self.factor

cdef class ElasticInOut(ElasticInterpolationBase):
    cdef double evaluate(self, double x):
        if x <= 0.5:
            x *= 2
            return pow(self.base, self.exponent * (x - 1)) * sin(x * self.bounceFactor) * self.factor / 2
        else:
            x = (1 - x) * 2
            return 1 - pow(self.base, self.exponent * (x - 1)) * sin(x * self.bounceFactor) * self.factor / 2


# Bounce
#####################################################

cdef class BounceInterpolationBase(InterpolationBase):
    cdef:
        DoubleList widths, heights

    def __cinit__(self, int bounces, float base):
        cdef int amount = max(1, bounces + 1)

        cdef:
            double a = 2.0 ** (amount - 1.0)
            double b = 2.0 ** amount - 2.0 ** (amount - 2.0) - 1.0
            double c = a / b

        self.widths = DoubleList(length = amount)
        self.heights = DoubleList(length = amount)
        cdef int i
        for i in range(amount):
            self.widths.data[i] = c / 2.0 ** i
            self.heights.data[i] = self.widths.data[i] * base
        self.heights.data[0] = 1

    cdef double bounceOut(self, double x):
        x += self.widths[0] / 2
        cdef int i
        cdef double width = 0, height = 0
        for i in range(self.widths.length):
            width = self.widths[i]
            if x <= width:
                x /= width
                height = self.heights[i]
                break
            x -= width
        cdef double z = 4 / width * height * x
        return 1 - (z - z * x) * width

cdef class BounceIn(BounceInterpolationBase):
    cdef double evaluate(self, double x):
        return 1 - self.bounceOut(1 - x)

cdef class BounceOut(BounceInterpolationBase):
    cdef double evaluate(self, double x):
        return self.bounceOut(x)

cdef class BounceInOut(BounceInterpolationBase):
    cdef double evaluate(self, double x):
        if x <= 0.5:
            return (1 - self.bounceOut(1 - x * 2)) / 2
        else:
            return self.bounceOut(x * 2 - 1) / 2 + 0.5
