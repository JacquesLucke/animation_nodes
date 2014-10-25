import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *

class mn_CombineListsNode(Node, AnimationNode):
	bl_idname = "mn_CombineListsNode"
	bl_label = "Combine Lists"
	
	def setSocketTypes(self, context):
		self.setSocketType(self.listTypesProperty)	
		nodePropertyChanged(self, context)
	
	listTypes = [
		("FLOAT", "Float", ""),
		("STRING", "String", ""),
		("OBJECT", "Object", "") ]
	listTypesProperty = bpy.props.EnumProperty(name = "Type", items = listTypes, default = "OBJECT", update = setSocketTypes)
	
	def init(self, context):
		forbidCompiling()
		self.setSocketType(self.listTypesProperty)
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "listTypesProperty")
		
	def execute(self, input):
		output = {}
		combination = input["List 1"][:]
		combination.extend(input["List 2"])
		output["Both Lists"] = combination
		return output
		
	def setSocketType(self, type):
		forbidCompiling()
		self.inputs.clear()
		self.outputs.clear()
		if type == "FLOAT":
			self.inputs.new("mn_FloatListSocket", "List 1")
			self.inputs.new("mn_FloatListSocket", "List 2")
			self.outputs.new("mn_FloatListSocket", "Both Lists")
		elif type == "STRING":
			self.inputs.new("mn_StringListSocket", "List 1")
			self.inputs.new("mn_StringListSocket", "List 2")
			self.outputs.new("mn_StringListSocket", "Both Lists")
		elif type == "OBJECT":
			self.inputs.new("mn_ObjectListSocket", "List 1")
			self.inputs.new("mn_ObjectListSocket", "List 2")
			self.outputs.new("mn_ObjectListSocket", "Both Lists")
		allowCompiling()
