import random
import numpy
import mathutils
from .. utils.timing import measureTime

randomNumberCache = []
cacheSize = int(2e7)
numpy.random.seed(1234)
randomNumberCache = numpy.random.random(cacheSize)

def getRandomNumberCache():
    return randomNumberCache

def getRandom(seed):
    return randomNumberCache[seed % cacheSize]

def getUniformRandom(seed, min, max):
    return min + randomNumberCache[seed % cacheSize] * (max - min)

def getRandomColor(seed, hue = None, saturation = None, value = None):
    if hue is None: hue = getRandom(seed)
    if saturation is None: saturation = getRandom(seed + 1000)
    if value is None: value = getRandom(seed + 2000)

    color = mathutils.Color()
    color.hsv = hue, saturation, value
    return color
