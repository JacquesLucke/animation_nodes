import sys
random = __import__("random")
from mathutils import Vector, Euler, Quaternion, Color

from .. utils.limits cimport INT_MAX

def getUniformRandom(seed, min, max):
    return randomDouble_Range(seed, min, max)

def getRandomColor(seed = None, hue = None, saturation = None, value = None):
    if seed is None: random.seed()
    else: random.seed(seed)

    if hue is None: hue = random.random()
    if saturation is None: saturation = random.random()
    if value is None: value = random.random()

    color = Color()
    color.hsv = hue, saturation, value
    return color

def getRandom3DVector(seed, double size):
    cdef int _seed = seed % INT_MAX
    return Vector((
        randomDouble_Range(_seed + 542655, -size, size),
        randomDouble_Range(_seed + 765456, -size, size),
        randomDouble_Range(_seed + 123587, -size, size)
    ))

def getRandomNormalized3DVector(seed, double size):
    cdef float vector[3]
    cdef int _seed = seed % INT_MAX
    randomVector3_Normalized(_seed, vector, size)
    return Vector((vector[0], vector[1], vector[2]))

def randomNumberTuple(seed, int size, double scale):
    cdef int _seed = seed % INT_MAX
    cdef int i
    _seed *= 23412
    return tuple(randomDouble_UnitRange(_seed + i) * scale for i in range(size))

def uniformRandomDoubleWithTwoSeeds(seed1, seed2, double min, double max):
    return randomDouble_Range((seed1 * 674523 + seed2 * 3465284) % 0x7fffffff, min, max)