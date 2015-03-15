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
	
def getPossibleCameraName(name = "camera"):
	randomString = getRandomString(3)
	counter = 1
	while bpy.data.cameras.get(name + randomString + str(counter)) is not None:
		counter += 1
	return name + randomString + str(counter)
	
def getPossibleLampName(name = "lamp"):
	randomString = getRandomString(3)
	counter = 1
	while bpy.data.lamps.get(name + randomString + str(counter)) is not None:
		counter += 1
	return name + randomString + str(counter)
	
def getPossibleNodeName(nodeTree, name = "node"):
	randomString = getRandomString(3)
	counter = 1
	while nodeTree.nodes.get(name + randomString + str(counter)) is not None:
		counter += 1
	return name + randomString + str(counter)
	
def getPossibleSocketName(node, name = "socket"):
	randomString = getRandomString(3)
	counter = 1
	while node.inputs.get(name + randomString + str(counter)) or node.outputs.get(name + randomString + str(counter)):
		counter += 1
	return name + randomString + str(counter)
	
def convertVariableNameToUI(sourceName):
	tempName = ""

	for i, char in enumerate(sourceName):
		if i == 0:
			tempName += char.upper()
			continue
		lastChar = tempName[-1]
		if lastChar == " ":
			tempName += char.upper()
		elif lastChar.isalpha() and char.isnumeric():
			tempName += " " + char.upper()
		elif lastChar.isnumeric() and char.isalpha():
			tempName += " " + char.upper()
		elif lastChar.islower() and char.isupper():
			tempName += " " + char.upper()
		elif char == "_":
			tempName += " "
		else:
			tempName += char
			
	bindingWords = ["and", "of", "to", "from"]
	words = tempName.split()
	newName = ""
	for word in words:
		if word.lower() in bindingWords:
			word = word.lower()
		newName += " " + word
		
	return newName