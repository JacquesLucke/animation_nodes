import bpy
from mn_utils import *

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
	for item in bpy.context.scene.mn_settings.keyframes:
		keyframes.append((item.name, item.type))
	return keyframes
def getKeyframeType(name):
	for keyframe in getKeyframes():
		if keyframe[0] == name: return keyframe[1]
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
			return ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])

def hasKeyframe(object, name):
	type = getKeyframeType(name)
	propertyName = getKeyframePropertyName(name)
	try:
		if type == "Float":
			tmp = object[propertyName]
		if type == "Transforms":
			tmp = (object[propertyName + " location"], object[propertyName + " rotation"], object[propertyName + " scale"])
		return True
	except:
		return False
		
def drawKeyframeInput(layout, object, name):
	type = getKeyframeType(name)
	propertyName = getKeyframePropertyName(name)
	if hasKeyframe(object, name):
		if type == "Float":
			layout.prop(object, nameToPath(propertyName))
		if type == "Transforms":
			row = layout.row()
			col = row.column(align = True)
			
			col.label("Location")
			for i in range(3):
				col.prop(object, nameToPath(propertyName + " location"), index = i, text = "")
			col = row.column(align = True)
			
			col.label("Rotation")
			for i in range(3):
				col.prop(object, nameToPath(propertyName + " rotation"), index = i, text = "")
			col = row.column(align = True)
			
			col.label("Scale")
			for i in range(3):
				col.prop(object, nameToPath(propertyName + " scale"), index = i, text = "")
	else:
		layout.label("keyframe isn't set on this object")
		
			
			
class SetTransformsKeyframe(bpy.types.Operator):
	bl_idname = "mn.set_transforms_keyframe"
	bl_label = "Set Transforms Keyframe"
	
	keyframeName = bpy.props.StringProperty(default = "")

	def execute(self, context):
		selectedObjects = getSelectedObjects()
		for object in selectedObjects:
			setKeyframe(object, self.keyframeName, (object.location, object.rotation_euler, object.scale))
		return {'FINISHED'}