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

def randomNumberTuple(seed, int size, double scale):
    cdef int _seed = seed % 0x7fffffff
    cdef int i
    _seed *= 23412
    return tuple(randomNumber(_seed + i) * scale for i in range(size))

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

cdef double randomNumber_Positive(int x):
    '''Generate a random number between 0 and 1 using a seed'''
    x = (x<<13) ^ x
    return ((x * (x * x * 15731 + 789221) + 1376312589) & 0x7fffffff) / 2147483648.0
