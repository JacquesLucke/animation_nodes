import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_GetListElementNode(Node, AnimationNode):
	bl_idname = "mn_GetListElementNode"
	bl_label = "Get Element"
	
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
		list = input["List"]
		index = input["Index"]
		output["Element"] = None
		if len(list) > 0:
			output["Element"] = list[max(min(index, len(list) - 1), 0)]
		return output
		
	def setSocketType(self, type):
		forbidCompiling()
		self.inputs.clear()
		self.outputs.clear()
		if type == "FLOAT":
			self.inputs.new("mn_FloatListSocket", "List")
			self.inputs.new("mn_IntegerSocket", "Index")
			self.outputs.new("mn_FloatSocket", "Element")
		elif type == "STRING":
			self.inputs.new("mn_StringListSocket", "List")
			self.inputs.new("mn_IntegerSocket", "Index")
			self.outputs.new("mn_StringSocket", "Element")
		elif type == "OBJECT":
			self.inputs.new("mn_ObjectListSocket", "List")
			self.inputs.new("mn_IntegerSocket", "Index")
			self.outputs.new("mn_ObjectSocket", "Element")
		forbidCompiling()
