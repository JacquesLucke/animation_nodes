import random

randomNumberCacheSize = 7919
randomNumberCache = []
random.seed(5827)
for i in range(randomNumberCacheSize):
    randomNumberCache.append(random.random())
    
def getRandom(seed):
    return randomNumberCache[seed % randomNumberCacheSize]
def getUniformRandom(seed, min, max):
    return min + randomNumberCache[seed % randomNumberCacheSize] * (max - min)