import random
import numpy
from .. utils.timing import measureTime

randomNumberCache = []
cacheSize = int(2e7)
randomNumberCache = numpy.random.random(cacheSize)

def getRandomNumberCache():
    return randomNumberCache

def getRandom(seed):
    return randomNumberCache[seed % cacheSize]

def getUniformRandom(seed, min, max):
    return min + randomNumberCache[seed % cacheSize] * (max - min)
