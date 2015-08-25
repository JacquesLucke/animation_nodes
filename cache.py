import random

# generic execution cache
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
