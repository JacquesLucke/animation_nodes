import bpy, random
from animation_nodes.mn_utils import *
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

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
		
		update = layout.operator("mn.update_text_separation_node", text = "Update", icon = "FILE_REFRESH")
		update.nodeTreeName = self.id_data.name
		update.nodeName = self.name
		
	def execute(self):
		textObjects = []
		for object in bpy.context.scene.objects:
			if self.isObjectPartOfThisNode(object):
				textObjects[getattr(object, indexPropertyName, 0)] = object
		return textObjects
		
	def updateSeparation(self):
		self.removeExistingObjects()
		self.createNewNodeID()
		
		source = bpy.data.objects.get(self.sourceObjectName);
		if source.type != "FONT":
			return
		
		
	def removeExistingObjects(self):
		deselectAll()
		for object in bpy.context.scene.objects:
			if self.isObjectPartOfThisNode(object):
				object.select = True
		bpy.ops.object.delete()
		
	def createNewNodeID(self):
		self.currentID = round(random.random() * 100000)
		
	def isObjectPartOfThisNode(self, object):
		return getattr(object, idPropertyName, -1) == self.currentID
		
class UpdateTextSeparationNode(bpy.types.Operator):
	bl_idname = "mn.update_text_separation_node"
	bl_label = "Update Text Separation"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
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

