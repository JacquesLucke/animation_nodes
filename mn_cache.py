from mn_utils import *

# generic cache
###############################

executionCache = {}

def clearExecutionCache():
	global executionCache
	executionCache = {}
	
def setExecutionCache(node, object):
	global executionCache
	executionCache[getNodeIdentifier(node)] = object
	
def getExecutionCache(node):
	identifier = getNodeIdentifier(node)
	if identifier in executionCache:
		return executionCache[identifier]
	return None
	

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