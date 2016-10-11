cimport cython

PI_HALF = PI / 2.0
PI_QUARTER = PI / 4.0

cdef double add(double x, double y):
    return x + y

cdef double subtract(double x, double y):
    return x - y

cdef double multiply(double x, double y):
    return x * y

@cython.cdivision(True)
cdef double divide_Save(double x, double y):
    return x / y if y != 0 else 0

cdef double modulo_Save(double x, double y):
    # cannot use cdivision(True) because it changes the modulo behavior
    # http://stackoverflow.com/a/3883019/4755171
    if y != 0: return x % y
    return 0

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

cdef double min(double x, double y):
    if x < y: return x
    else: return y

cdef double max(double x, double y):
    if x > y: return x
    else: return y

cdef double abs(double x):
    if x < 0: return -x
    else: return x
