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

def getUniformRandom(seed, min, max):
    return min + randomNumberCache[seed % cacheSize] * (max - min)

def getRandomColor(seed = None, hue = None, saturation = None, value = None):
    if seed is None: random.seed()
    else: random.seed(seed)

    if hue is None: hue = random.random()
    if saturation is None: saturation = random.random()
    if value is None: value = random.random()

    color = mathutils.Color()
    color.hsv = hue, saturation, value
    return color
