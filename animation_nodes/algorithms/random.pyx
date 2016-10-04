import sys
import numpy
random = __import__("random")
from mathutils import Vector, Euler, Quaternion, Color

def getUniformRandom(seed, min, max):
    return uniformRandomNumber(seed, min, max)

def getRandomColor(seed = None, hue = None, saturation = None, value = None):
    if seed is None: random.seed()
    else: random.seed(seed)

    if hue is None: hue = random.random()
    if saturation is None: saturation = random.random()
    if value is None: value = random.random()

    color = Color()
    color.hsv = hue, saturation, value
    return color

def uniformRandomVectorWithTwoSeeds(seed1, seed2, double scale):
    cdef int seed = (seed1 * 1234365 + seed2 * 8672234) % 0x7fffffff
    return Vector((
            uniformRandomNumber(seed + 0, -scale, scale),
            uniformRandomNumber(seed + 1, -scale, scale),
            uniformRandomNumber(seed + 2, -scale, scale)))

def uniformRandomEulerWithTwoSeeds(seed1, seed2, double scale):
    cdef int seed = (seed1 * 646735 + seed2 * 2346547) % 0x7fffffff
    return Euler((
            uniformRandomNumber(seed + 0, -scale, scale),
            uniformRandomNumber(seed + 1, -scale, scale),
            uniformRandomNumber(seed + 2, -scale, scale)))

def uniformRandomQuaternionWithTwoSeeds(seed1, seed2, double scale):
    cdef int seed = (seed1 * 9783452 + seed2 * 1235786) % 0x7fffffff
    return Quaternion((1,
            uniformRandomNumber(seed + 0, -scale, scale),
            uniformRandomNumber(seed + 1, -scale, scale),
            uniformRandomNumber(seed + 2, -scale, scale)))

def uniformRandomNumberWithTwoSeeds(seed1, seed2, double min, double max):
    return uniformRandomNumber((seed1 * 674523 + seed2 * 3465284) % 0x7fffffff, min, max)

cdef int uniformRandomInteger(int x, int min, int max):
    return <int>uniformRandomNumber(x, min, <double>max + 0.9999999)

cdef double uniformRandomNumber(int x, double min, double max):
    '''Generate a random number between min and max using a seed'''
    x = (x<<13) ^ x
    return ((x * (x * x * 15731 + 789221) + 1376312589) & 0x7fffffff) / 2147483648.0 * (max - min) + min

cdef double randomNumber(int x):
    '''Generate a random number between -1 and 1 using a seed'''
    x = (x<<13) ^ x
    return 1.0 - ((x * (x * x * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0
