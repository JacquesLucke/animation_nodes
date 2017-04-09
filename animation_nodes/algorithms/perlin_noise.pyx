from libc.limits cimport INT_MAX
from . random cimport randomNumber
from .. data_structures cimport Vector3DList

# http://freespace.virgin.net/hugo.elias/models/m_perlin.htm

def perlinNoiseVectorForNodes(seed, nodeSeed, double evolution, double speed, amplitude, octaves, double persistance):
    cdef double finalX = evolution * max(speed, 0) / 20 + seed * 9234612 + nodeSeed * 3424533
    cdef int finalOctaves = max(octaves, 0) % 0x7fffffff
    return (perlinNoise1D(finalX, persistance, finalOctaves) * amplitude[0],
            perlinNoise1D(finalX + 1356453, persistance, finalOctaves) * amplitude[1],
            perlinNoise1D(finalX + 9786652, persistance, finalOctaves) * amplitude[2])

def perlinNoiseForNodes(seed, nodeSeed, double evolution, double speed, double amplitude, octaves, double persistance):
    cdef double finalX = evolution * max(speed, 0) / 20 + seed * 545621 + nodeSeed * 3424536
    return perlinNoise1D(finalX, persistance, octaves % 0x7fffffff) * amplitude

def wiggleVectorList(amount, double evolution, amplitude, int octaves, double persistance):
    cdef Vector3DList result = Vector3DList(length = amount)
    cdef float *values = <float*>result.data
    cdef float _amplitude[3]
    cdef Py_ssize_t i
    _amplitude[0], _amplitude[1], _amplitude[2] = amplitude[0], amplitude[1], amplitude[2]
    for i in range(amount * 3):
        values[i] = perlinNoise1D(evolution + i * 354623, persistance, octaves) * _amplitude[i % 3]
    return result

cpdef double perlinNoise1D(double x, double persistance, int octaves):
    cdef:
        double total = 0
        double frequency
        double amplitude
        int i

    for i in range(octaves):
        frequency = 2**i
        amplitude = persistance**i
        total += interpolatedNoise(x * frequency) * amplitude

    return total

cdef double interpolatedNoise(double x):
    x = x % INT_MAX
    cdef:
        int intX = int(x)
        double fracX = x - intX
        double v0 = randomNumber(intX - 2)
        double v1 = randomNumber(intX - 1)
        double v2 = randomNumber(intX)
        double v3 = randomNumber(intX + 1)
        double v4 = randomNumber(intX + 2)
        double v5 = randomNumber(intX + 3)

    return cubicInterpolation(
            v0 / 4.0 + v1 / 2.0 + v2 / 4.0,
            v1 / 4.0 + v2 / 2.0 + v3 / 4.0,
            v2 / 4.0 + v3 / 2.0 + v4 / 4.0,
            v3 / 4.0 + v4 / 2.0 + v5 / 4.0,
            fracX)

cdef double cubicInterpolation(double v0, double v1, double v2, double v3, double x):
    cdef double p, q, r, s
    p = (v3 - v2) - (v0 - v1)
    q = (v0 - v1) - p
    r = v2 - v0
    s = v1
    return p * x**3 + q * x**2 + r * x + s
