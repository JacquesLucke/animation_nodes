from . random cimport randomNumber

# http://freespace.virgin.net/hugo.elias/models/m_perlin.htm

def perlinNoiseVectorForNodes(seed, nodeSeed, double evolution, double speed, amplitude, octaves, double persistance):
    cdef double finalX = evolution * max(speed, 0) / 20 + seed * 9234612 + nodeSeed * 3424533
    cdef int finalOctaves = octaves % 0x7fffffff
    return (perlinNoise(finalX, persistance, finalOctaves) * amplitude[0],
            perlinNoise(finalX + 1356453, persistance, finalOctaves) * amplitude[1],
            perlinNoise(finalX + 9786652, persistance, finalOctaves) * amplitude[2])

def perlinNoiseForNodes(seed, nodeSeed, double evolution, double speed, double amplitude, octaves, double persistance):
    cdef double finalX = evolution * max(speed, 0) / 20 + seed * 545621 + nodeSeed * 3424536
    return perlinNoise(finalX, persistance, octaves % 0x7fffffff) * amplitude

cpdef double perlinNoise(double x, double persistance, int octaves):
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
