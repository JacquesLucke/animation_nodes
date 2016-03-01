import numpy
import random
from mathutils import Vector, Color
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

    color = Color()
    color.hsv = hue, saturation, value
    return color

def getRandomVectors(seed, amount):
    numpy.random.seed(seed)
    return [Vector(v) for v in numpy.random.random([amount, 3])]
