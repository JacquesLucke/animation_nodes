import bpy, random
from animation_nodes.mn_utils import *
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mathutils import Vector, Matrix

idPropertyName = "text separation node id"
indexPropertyName = "text separation node index"

class mn_SeparateTextObject(Node, AnimationNode):
	bl_idname = "mn_SeparateTextObject"
	bl_label = "Separate Text Object"
	
	sourceObjectName = bpy.props.StringProperty(name = "Source Object")
	currentID = bpy.props.IntProperty(default = 0);
	objectCount = bpy.props.IntProperty(default = 0);
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_ObjectListSocket", "Text Objects")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Text Objects" : "textObjects"}
		
	def draw_buttons(self, context, layout):
		row = layout.row(align = True)
		row.prop(self, "sourceObjectName", text = "Source")
		assign = row.operator("mn.assign_active_object_to_text_separation_node", icon = "EYEDROPPER", text = "")
		assign.nodeTreeName = self.id_data.name
		assign.nodeName = self.name
		
		source = self.getSourceObject()
		if source is not None:
			row.prop(source, "hide", text = "")
		
		update = layout.operator("mn.update_text_separation_node", text = "Update", icon = "FILE_REFRESH")
		update.nodeTreeName = self.id_data.name
		update.nodeName = self.name
		
	def execute(self):
		textObjects = [None] * self.objectCount
		for object in bpy.context.scene.objects:
			if self.isObjectPartOfThisNode(object):
				textObjects[getattr(object, '["'+indexPropertyName+'"]', 0)] = object
		return textObjects
		
	def updateSeparation(self):
		self.removeExistingObjects()
		self.createNewNodeID()
		
		source = self.getSourceObject()
		if source is None: return
		if source.data is None: return
		source.hide = False
		
		objects = splitTextObject(source)
		for i, object in enumerate(objects):
			object[idPropertyName] = self.currentID
			object[indexPropertyName] = i
		self.objectCount = len(objects)
		
		source.hide = True
		
	def removeExistingObjects(self):
		deselectAll()
		for object in bpy.context.scene.objects:
			if self.isObjectPartOfThisNode(object):
				object.select = True
		bpy.ops.object.delete()
		
	def createNewNodeID(self):
		self.currentID = round(random.random() * 100000)
		
	def isObjectPartOfThisNode(self, object):
		return getattr(object, '["'+idPropertyName+'"]', -1) == self.currentID
	def getSourceObject(self):
		source = bpy.data.objects.get(self.sourceObjectName)
		if getattr(source, "type", "") == "FONT": return source
		return None
		
	def copy(self, node):
		self.createNewNodeID()
		
def splitTextObject(source):
	text = cleanText(source.data.body)
	
	splineCounter = 0
	sourceSplinePositions = getSplinePositions(source)
	objects = []
	
	for i, character in enumerate(text):
		name = source.name + " part " + str(i)
		characterObject = newCharacterObject(name, source.data, character)

		characterSplinePositions = getSplinePositions(characterObject)
		test = characterSplinePositions[0]
		setCharacterPosition(characterObject, source, sourceSplinePositions[splineCounter], characterSplinePositions[0])
		splineCounter += len(characterSplinePositions)
		
		objects.append(characterObject)
		
	return objects
	
def cleanText(text):
	for part in [" ", "\n", "\t", "\r"]:
		text = text.replace(part, "");
	return text
		
def newCharacterObject(name, sourceData, character):
	newTextData = sourceData.copy()
	newTextData.body = character
	characterObject = bpy.data.objects.new(name, newTextData)
	bpy.context.scene.objects.link(characterObject)
	return characterObject
	
def setCharacterPosition(characterObject, source, sourceSplinePosition, offsetPosition):	
	characterOffset = sourceSplinePosition - offsetPosition
	characterObject.matrix_world = source.matrix_world * Matrix.Translation(characterOffset)
		
def getSplinePositions(textObject):
	onlySelect(textObject)
	curve = newCurveFromActiveObject()
	positions = [Vector(spline.bezier_points[0].co) for spline in curve.data.splines]
	removeCurve(curve)
	return positions

def onlySelect(object):
	bpy.ops.object.select_all(action = "DESELECT")
	bpy.context.scene.objects.active = object
	object.select = True
	
def newCurveFromActiveObject():
	bpy.ops.object.convert(target = "CURVE", keep_original = True)
	return bpy.context.scene.objects.active
	
def removeCurve(curve):
	curveData = curve.data
	bpy.context.scene.objects.unlink(curve)
	bpy.data.objects.remove(curve)
	bpy.data.curves.remove(curveData)
		
class UpdateTextSeparationNode(bpy.types.Operator):
	bl_idname = "mn.update_text_separation_node"
	bl_label = "Update Text Separation"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
		
	def execute(self, context):
		obj = getActive()
		node = getNode(self.nodeTreeName, self.nodeName)
		node.updateSeparation()
		return {'FINISHED'}		

class AssignActiveObjectToTextSeparationNode(bpy.types.Operator):
	bl_idname = "mn.assign_active_object_to_text_separation_node"
	bl_label = "Assign Active Object"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		obj = getActive()
		node = getNode(self.nodeTreeName, self.nodeName)
		node.sourceObjectName = obj.name
		return {'FINISHED'}		

