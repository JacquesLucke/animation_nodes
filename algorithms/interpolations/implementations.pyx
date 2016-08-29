from libc.math cimport M_PI as PI
from libc.math cimport pow, sqrt, sin, cos
from ... data_structures cimport InterpolationBase, DoubleList

'''
Here is a good source for different interpolation functions in Java:
https://github.com/libgdx/libgdx/blob/master/gdx/src/com/badlogic/gdx/math/Interpolation.java
'''

# Linear
#####################################################

cdef class Linear(InterpolationBase):
    def __cinit__(self):
        self.clamped = True

    cdef double evaluate(self, double x):
        return x


# Power
#####################################################

cdef class PowerIn(InterpolationBase):
    cdef int exponent

    def __cinit__(self, int exponent):
        self.exponent = max(exponent, 1)
        self.clamped = True

    cdef double evaluate(self, double x):
        return pow(x, self.exponent)

cdef class PowerOut(InterpolationBase):
    cdef int exponent
    cdef int factor

    def __cinit__(self, int exponent):
        self.exponent = max(exponent, 1)
        self.factor = -1 if self.exponent % 2 == 0 else 1
        self.clamped = True

    cdef double evaluate(self, double x):
        return pow(x - 1, self.exponent) * self.factor + 1

cdef class PowerInOut(InterpolationBase):
    cdef int exponent
    cdef double factor

    def __cinit__(self, int exponent):
        self.exponent = max(exponent, 1)
        self.factor = -0.5 if self.exponent % 2 == 0 else 0.5
        self.clamped = True

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
        self.clamped = True

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

cdef class CircularInterpolationBase(InterpolationBase):
    def __cinit__(self):
        self.clamped = True

cdef class CircularIn(CircularInterpolationBase):
    cdef double evaluate(self, double x):
        return 1 - sqrt(1 - x * x)

cdef class CircularOut(CircularInterpolationBase):
    cdef double evaluate(self, double x):
        x -= 1
        return sqrt(1 - x * x)

cdef class CircularInOut(CircularInterpolationBase):
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
        self.clamped = True

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


# Back
#####################################################

cdef class BackInterpolationBase(InterpolationBase):
    cdef double scale

    def __cinit__(self, double scale):
        self.scale = scale

cdef class BackIn(BackInterpolationBase):
    cdef double evaluate(self, double x):
        return x * x * ((self.scale + 1) * x - self.scale)

cdef class BackOut(BackInterpolationBase):
    cdef double evaluate(self, double x):
        x -= 1
        return x * x * ((self.scale + 1) * x + self.scale) + 1

cdef class BackInOut(BackInterpolationBase):
    cdef double evaluate(self, double x):
        if x <= 0.5:
            x *= 2
            return x * x * ((self.scale + 1) * x - self.scale) / 2
        else:
            x = (x - 1) * 2
            return x * x * ((self.scale + 1) * x + self.scale) / 2 + 1


# Sine
#####################################################

cdef class SinInterpolationBase(InterpolationBase):
    def __cinit__(self):
        self.clamped = True

cdef class SinIn(SinInterpolationBase):
    cdef double evaluate(self, double x):
        return 1.0 - cos(x * PI / 2.0)

cdef class SinOut(SinInterpolationBase):
    cdef double evaluate(self, double x):
        return sin(x * PI / 2.0)

cdef class SinInOut(SinInterpolationBase):
    cdef double evaluate(self, double x):
        return (1.0 - cos(x * PI)) / 2.0


# Specials
#####################################################

cdef class Mixed(InterpolationBase):
    cdef:
        double factor
        InterpolationBase a, b

    def __cinit__(self, double factor, InterpolationBase a not None, InterpolationBase b not None):
        self.factor = factor
        self.a = a
        self.b = b
        self.clamped = a.clamped and b.clampd and 0 <= factor <= 1

    cdef double evaluate(self, double x):
        return self.a.evaluate(x) * (1 - self.factor) + self.b.evaluate(x) * self.factor


cdef class PyInterpolation(InterpolationBase):
    cdef object function

    def __cinit__(self, object function not None):
        if not hasattr(function, "__call__"):
            raise TypeError("object is not callable")
        self.function = function

    cdef double evaluate(self, double x):
        return self.function(x)


from bpy.types import FCurve

cdef class FCurveMapping(InterpolationBase):
    cdef:
        object fCurve
        double xMove, xFactor, yMove, yFactor

    def __cinit__(self, object fCurve, double xMove, double xFactor, double yMove, double yFactor):
        if not isinstance(fCurve, FCurve):
            raise TypeError("Expected FCurve")
        self.fCurve = fCurve
        self.xMove = xMove
        self.xFactor = xFactor
        self.yMove = yMove
        self.yFactor = yFactor

    cdef double evaluate(self, double x):
        x = x * self.xFactor + self.xMove
        return (self.fCurve.evaluate(x) + self.yMove) * self.yFactor
