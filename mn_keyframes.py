import bpy
from mathutils import Vector
from animation_nodes.mn_utils import *

keyframePropertyPrefix = "Animation Nodes - "

keyframeTypes = ["Float", "Transforms", "Vector"]
	
def getKeyframeTypeItems(self = None, context = None):
	items = []
	for type in keyframeTypes:
		items.append((type, type, ""))
	return items
def getKeyframeNameItems(self = None, context = None):
	items = []
	for name, type in getKeyframes():
		items.append((name, name, type))
	return items
def getKeyframeNames():
	names = []
	for name, type in getKeyframes():
		names.append(name)
	return names
	
def newKeyframe(name, type):
	if not isKeyframeNameUsed(name):
		item = bpy.context.scene.mn_settings.keyframes.keys.add()
		item.name = name
		item.type = type
def removeKeyframe(name):	
	item = None
	for i, item in enumerate(bpy.context.scene.mn_settings.keyframes.keys):
		if item.name == name: break
	if item is not None:
		bpy.context.scene.mn_settings.keyframes.keys.remove(i)

def getKeyframes():
	keyframes = []
	keyframes.append(("Initial Transforms", "Transforms"))
	for item in bpy.context.scene.mn_settings.keyframes.keys:
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
	elif type == "Vector":
		object[propertyName] = data
		
def getKeyframe(object, name, type = None):
	if type is None: type = getKeyframeType(name)
	propertyName = getKeyframePropertyName(name)
	try:
		if type == "Float":
			return object[propertyName]
		elif type == "Transforms":
			transforms = []
			transforms.append(Vector(object[propertyName + " location"]))
			transforms.append(Vector(object[propertyName + " rotation"]))
			transforms.append(Vector(object[propertyName + " scale"]))
			return transforms
		elif type == "Vector":
			return Vector(object[propertyName])
	except:
		if type == "Float":
			return 0.0
		elif type == "Transforms":
			return (Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 0.0)), Vector((1.0, 1.0, 1.0)))
		elif type == "Vector":
			return Vector([0, 0, 0])

def isKeyframeNameUsed(name):
	for keyframe in getKeyframes():
		if keyframe[0] == name: return True
	return False
			
def hasKeyframe(object, name):
	type = getKeyframeType(name)
	propertyName = getKeyframePropertyName(name)
	try:
		if type in ["Float", "Vector"]:
			tmp = object[propertyName]
		elif type == "Transforms":
			tmp = (object[propertyName + " location"], object[propertyName + " rotation"], object[propertyName + " scale"])
		return True
	except:
		return False
		
def removeKeyframeFromObject(object, name):
	type = getKeyframeType(name)
	propertyName = getKeyframePropertyName(name)
	try:
		if type in ["Float", "Vector"]:
			del object[propertyName]
		elif type == "Transforms":
			del object[propertyName + " location"]
			del object[propertyName + " rotation"]
			del object[propertyName + " scale"]
	except: pass
		
def drawKeyframeInput(layout, object, name):
	type = getKeyframeType(name)
	propertyName = getKeyframePropertyName(name)
	if hasKeyframe(object, name):
		if type == "Float":
			layout.prop(object, nameToPath(propertyName), text = "Value")
		elif type == "Transforms":
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
		elif type == "Vector":
			layout.prop(object, nameToPath(propertyName), text = "")
	else:
		layout.label("keyframe isn't set on this object")
		
		

class SetFloatKeyframe(bpy.types.Operator):
	bl_idname = "mn.set_float_keyframe"
	bl_label = "Set Float Keyframe"
	
	keyframeName = bpy.props.StringProperty(default = "")
	dataPath = bpy.props.StringProperty(default = "")

	def execute(self, context):
		selectedObjects = getSelectedObjects()
		for object in selectedObjects:
			try: value = float(eval("object." + self.dataPath))
			except: value = 0.0
			setKeyframe(object, self.keyframeName, value)
		return {'FINISHED'}		
			
class SetTransformsKeyframe(bpy.types.Operator):
	bl_idname = "mn.set_transforms_keyframe"
	bl_label = "Set Transforms Keyframe"
	
	keyframeName = bpy.props.StringProperty(default = "")

	def execute(self, context):
		selectedObjects = getSelectedObjects()
		for object in selectedObjects:
			setKeyframe(object, self.keyframeName, (object.location, object.rotation_euler, object.scale))
		return {'FINISHED'}
		
class SetVectorKeyframeFromPath(bpy.types.Operator):
	bl_idname = "mn.set_vector_keyframe_from_path"
	bl_label = "Set Vector Keyframe"
	
	keyframeName = bpy.props.StringProperty(default = "")
	vectorPath = bpy.props.StringProperty(default = "location")

	def execute(self, context):
		selectedObjects = getSelectedObjects()
		for object in selectedObjects:
			setKeyframe(object, self.keyframeName, getattr(object, self.vectorPath, [0, 0, 0]))
		return {'FINISHED'}
		
class RemoveKeyframeFromObject(bpy.types.Operator):
	bl_idname = "mn.remove_keyframe_from_object"
	bl_label = "Remove Keyframe From Object"
	
	objectName = bpy.props.StringProperty(default = "")
	keyframeName = bpy.props.StringProperty(default = "")

	def execute(self, context):
		object = bpy.data.objects.get(self.objectName)
		if object is not None:
			removeKeyframeFromObject(object, self.keyframeName)
		return {'FINISHED'}
		
class RemoveKeyframe(bpy.types.Operator):
	bl_idname = "mn.remove_keyframe"
	bl_label = "Remove Keyframe"
	
	keyframeName = bpy.props.StringProperty(default = "")

	def execute(self, context):
		removeKeyframe(self.keyframeName)
		return {'FINISHED'}
			
class NewKeyframe(bpy.types.Operator):
	bl_idname = "mn.new_keyframe"
	bl_label = "New Keyframe"
	
	keyframeName = bpy.props.StringProperty(default = "temp")
	keyframeType = bpy.props.StringProperty(default = "Float")

	def execute(self, context):
		newKeyframe(self.keyframeName, self.keyframeType)
		return {'FINISHED'}

