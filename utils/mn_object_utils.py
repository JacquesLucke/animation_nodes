import bpy
from mn_utils import *

def getObjectTransformsAtFrame(object, frame):
	location = [0, 0, 0]
	rotation = [0, 0, 0]
	scale = [1, 1, 1]
	
	for i in range(3):	
		location[i] = getValueAtFrame(object, "location", i, frame)
	for i in range(3):	
		rotation[i] = getValueAtFrame(object, "rotation_euler", i, frame)
	for i in range(3):	
		scale[i] = getValueAtFrame(object, "scale", i, frame)
	return location, rotation, scale
		
def getValueAtFrame(object, dataPath, index, frame):
	fCurve = getFCurveWithDataPath(object, dataPath = dataPath, index = index)
	if fCurve is None:
		return eval("object." + dataPath + "[" + str(index) + "]")
	else:
		return fCurve.evaluate(frame)
	
def getFrameChange(object, frame, dataPath, index):
	fCurve = getFCurveWithDataPath(object, dataPath = dataPath, index = index)
	if fCurve is None:
		return 0
	else:
		return fCurve.evaluate(frame) - fCurve.evaluate(frame - 1)