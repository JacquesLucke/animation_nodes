import bpy
from animation_nodes.mn_utils import *

def getPossibleObjectName(name = "object"):
	randomString = getRandomString(3)
	counter = 1
	while bpy.data.objects.get(name + randomString + str(counter)) is not None:
		counter += 1
	return name + randomString + str(counter)
	
def getPossibleCurveName(name = "curve"):
	randomString = getRandomString(3)
	counter = 1
	while bpy.data.curves.get(name + randomString + str(counter)) is not None:
		counter += 1
	return name + randomString + str(counter)

def getPossibleMeshName(name = "mesh"):
	randomString = getRandomString(3)
	counter = 1
	while bpy.data.meshes.get(name + randomString + str(counter)) is not None:
		counter += 1
	return name + randomString + str(counter)
	
def getPossibleNodeName(nodeTree, name = "node"):
	randomString = getRandomString(3)
	counter = 1
	while nodeTree.nodes.get(name + randomString + str(counter)) is not None:
		counter += 1
	return name + randomString + str(counter)