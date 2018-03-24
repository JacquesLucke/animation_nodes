cdef int uniformRandomInteger(int x, int min, int max)
cdef double uniformRandomDouble(int x, double min, double max)
cdef float uniformRandomFloat(int x, float min, float max)
cdef void randomNormalized3DVector(int seed, float *vector, float size)

cdef double randomNumber(int x)

cdef inline double randomDouble_Positive(int x):
    '''Generate a random number between 0 and 1 using a seed'''
    x = (x<<13) ^ x
    return ((x * (x * x * 15731 + 789221) + 1376312589) & 0x7fffffff) / 2147483648.0

cdef inline float randomFloat_Positive(int x):
    '''Generate a random number between 0 and 1 using a seed'''
    x = (x<<13) ^ x
    return ((x * (x * x * 15731 + 789221) + 1376312589) & 0x7fffffff) / 2147483648.0