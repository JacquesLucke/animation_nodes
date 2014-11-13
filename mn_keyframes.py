import bpy

keyframePropertyPrefix = "Animation Nodes - "

keyframeTypes = ["Float", "Transforms"]
	
def getKeyframeTypeItems():
	items = []
	for type in keyframeTypes:
		items.append((type, type, ""))
	return items

def getKeyframes():
	keyframes = []
	keyframes.append(("Initial Transforms", "Transforms"))
	for item in bpy.context.scene.keyframes:
		keyframes.append((item.name, item.type))
	return keyframes
def getKeyframeType(name):
	for item in bpy.context.scene.keyframes:
		if item.name == name: return item.type
	return None
def getKeyframePropertyName(name):
	return keyframePropertyPrefix + name
	
def setKeyframe(object, name, data):
	if object is None: return False
	type = getKeyframeType(name)
	if type not in keyframeTypes: return False
	
	propertyName = getKeyframePropertyName(name)
	
	if type == "Float":
		object[propertyName] = data
	elif type == "Transforms":
		object[propertyName + " location"] = data[0]
		object[propertyName + " rotation"] = data[1]
		object[propertyName + " scale"] = data[2]
		
def getKeyframe(object, name):
	type = getKeyframeType(name)
	propertyName = getKeyframePropertyName(name)
	try:
		if type == "Float":
			return object[propertyName]
		elif type == "Transforms":
			transforms = []
			transforms.append(object[propertyName + " location"])
			transforms.append(object[propertyName + " rotation"])
			transforms.append(object[propertyName + " scale"])
			return transforms
	except:
		if type == "Float":
			return 0
		elif type == "Transforms":
			return ([0, 0, 0], [0, 0, 0], [1, 1, 1])