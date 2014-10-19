import bpy
from mn_utils import *
from mn_cache import *

def getObjectTransformsAtFrame(object, frame):
	location = getArrayValueAtFrame(object, "location", frame)
	rotation = getArrayValueAtFrame(object, "rotation_euler", frame)
	scale = getArrayValueAtFrame(object, "scale", frame)
	return location, rotation, scale
	
# get value in one frame

def getArrayValueAtFrame(object, dataPath, frame, arraySize = 3):
	fCurves = getFCurvesWithDataPath(object, dataPath)
	values = [0] * arraySize
	for index in range(arraySize):
		fCurve = getFCurveWithIndex(fCurves, index)
		if fCurve is None: values[index] = getattr(object, dataPath)[index]
		else: values[index] = fCurve.evaluate(frame)
	return values
	
def getSingleValueAtFrame(object, dataPath, frame):
	fCurves = getFCurvesWithDataPath(object, dataPath)
	if len(fCurves) == 0:
		return getattr(object, dataPath)
	return fCurves[0].evaluate(frame)
	
def getSingleValueOfArrayAtFrame(object, dataPath, index, frame):
	fCurves = getFCurvesWithDataPath(object, dataPath)
	fCurve = getFCurveWithIndex(fCurves, index)
	if fCurve is None: return getattr(object, dataPath)[index]
	return fCurve.evaluate(frame)
	
	
# get values of multiple frames

def getArrayValueAtMultipleFrames(object, dataPath, frames, arraySize = 3):
	values = [0] * len(frames)
	for i in range(len(frames)): values[i] = [0] * arraySize
	fCurves = getFCurvesWithDataPath(object, dataPath)
	for index in range(arraySize):
		fCurve = getFCurveWithIndex(fCurves, index)
		if fCurve is None:
			value = getattr(object, dataPath)[index]
			for i, frame in enumerate(frames):
				values[i][index] = value
		else:
			for i, frame in enumerate(frames):
				values[i][index] = fCurve.evaluate(frame)
	return values
		
def getFCurveWithIndex(fCurves, index):
	for fCurve in fCurves:
		if fCurve.array_index == index: return fCurve
	return None
	

def getFCurvesWithDataPath(object, dataPath):
	identifier = object.type + object.name + dataPath
	cache = getExecutionCache(identifier)
	if cache is None:
		fCurves = []
		if hasActionData(object):
			for fCurve in object.animation_data.action.fcurves:
				if fCurve.data_path == dataPath:
					fCurves.append(fCurve)
		cache = fCurves
		setExecutionCache(identifier, cache)
	return cache
	
	
	
	
	
	
	
	
	
		
def getValueAtFrame(object, dataPath, index, frame):
	fCurve = getFCurveWithDataPath(object, dataPath = dataPath, index = index)
	if fCurve is None:
		return eval("object." + dataPath + "[" + str(index) + "]")
	else:
		return fCurve.evaluate(frame)
		
def getPossibleObjectName(self, name = "object"):
	randomString = getRandomString(3)
	counter = 1
	while bpy.data.objects.get(name + randomString + str(counter)) is not None:
		counter += 1
	return name + randomString + str(counter)