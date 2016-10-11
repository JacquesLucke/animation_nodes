cimport cython

PI_HALF = PI / 2.0
PI_QUARTER = PI / 4.0

cdef double add(double a, double b):
    return a + b

cdef double subtract(double a, double b):
    return a - b

cdef double multiply(double a, double b):
    return a * b

@cython.cdivision(True)
cdef double divide_Save(double a, double b):
    return a / b if b != 0 else 0

cdef double asin_Save(double x):
    if x < -1: return -PI_HALF
    if x > 1: return PI_HALF
    return asin(x)

cdef double acos_Save(double x):
    if x < -1: return PI
    if x > 1: return 0
    return acos(x)

cdef double power_Save(double base, double exponent):
    if base >= 0 or exponent % 1 == 0:
        return pow(base, exponent)
    return 0
