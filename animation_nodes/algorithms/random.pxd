from libc.math cimport M_PI as PI
from libc.math cimport sqrt, sin, cos


cdef inline double randomDouble_Range(int x, double min, double max):
    return randomDouble_Positive(x) * (max - min) + min

cdef inline float randomFloat_Range(int x, float min, float max):
    return randomFloat_Positive(x) * (max - min) + min

cdef inline int randomInt_Range(int x, int min, int max):
    return <int>randomFloat_Range(x, min, max + 0.999999)


cdef inline double randomDouble_ScaledRange(int x, float scale):
    return randomInteger(x) / 2147483648.0 * scale

cdef inline float randomFloat_ScaledRange(int x, float scale):
    return randomInteger(x) / 2147483648.0 * scale

cdef inline double randomDouble_UnitRange(int x):
    return randomInteger(x) / 2147483648.0


cdef inline double randomDouble_Positive(int x):
    return (randomInteger(x) & 0x7fffffff) / 2147483648.0

cdef inline float randomFloat_Positive(int x):
    return (randomInteger(x) & 0x7fffffff) / 2147483648.0


cdef inline int randomInteger(int x):
    x = (x<<13) ^ x
    return (x * (x * x * 15731 + 789221) + 1376312589)



# more specific random generators
#######################################################

cdef inline void randomVector3_Normalized(int seed, float *vector, float size):
    cdef double a = randomDouble_Positive(seed) * 2 * PI
    cdef double b = randomDouble_UnitRange(seed + 234452)
    cdef double c = sqrt(1 - b * b)
    vector[0] = c * cos(a) * size
    vector[1] = c * sin(a) * size
    vector[2] = b * size