import bpy
from mn_utils import *

def getArrayValueAtFrame(object, dataPath, frame, arraySize = 3):
	fCurves = getFCurvesWithDataPath(object, dataPath)
	values = [0] * arraySize
	for index in range(arraySize):
		fCurve = getFCurveWithIndex(fCurves, index)
		if fCurve is None: 	values[index] = getattr(object, dataPath)[index]
		else: values[index] = fCurve.evaluate(frame)
	return values
		
def getFCurveWithIndex(fCurves, index):
	for fCurve in fCurves:
		if fCurve.array_index == index: return fCurve
	return None

def getObjectTransformsAtFrame(object, frame):
	location = getArrayValueAtFrame(object, "location", frame)
	rotation = getArrayValueAtFrame(object, "rotation_euler", frame)
	scale = getArrayValueAtFrame(object, "scale", frame)
	return location, rotation, scale
		
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