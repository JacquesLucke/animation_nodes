from mn_utils import *
import random

# generic cache
###############################

executionCache = {}

def clearExecutionCache():
	global executionCache
	executionCache = {}
	
def setExecutionCache(identifier, object):
	global executionCache
	executionCache[identifier] = object
	
def getExecutionCache(identifier):
	return executionCache.get(identifier)
	

# random number cache
###############################

randomNumberCacheSize = 7919
randomNumberCache = []
random.seed(5827)
for i in range(randomNumberCacheSize):
	randomNumberCache.append(random.random())
	
	
def getRandom(seed):
	return randomNumberCache[seed % randomNumberCacheSize]
def getUniformRandom(seed, min, max):
	return min + randomNumberCache[seed % randomNumberCacheSize] * (max - min)