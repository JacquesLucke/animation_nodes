from mn_utils import *

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