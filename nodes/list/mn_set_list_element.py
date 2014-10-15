import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class SetListElementNode(Node, AnimationNode):
	bl_idname = "SetListElementNode"
	bl_label = "Set Element"
	
	clampIndex = bpy.props.BoolProperty(default = True)
	
	def setSocketTypes(self, context):
		self.setSocketType(self.listTypesProperty)	
		nodePropertyChanged(self, context)
	
	listTypes = [
		("FLOAT", "Float", ""),
		("STRING", "String", ""),
		("OBJECT", "Object", "") ]
	listTypesProperty = bpy.props.EnumProperty(name = "Type", items = listTypes, default = "OBJECT", update = setSocketTypes)
	
	def init(self, context):
		self.setSocketType(self.listTypesProperty)
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "listTypesProperty")
		layout.prop(self, "clampIndex", text = "Clamp Index")
		
	def execute(self, input):
		output = {}
		list = input["List"]
		index = max(min(input["Index"], len(list) - 1), 0)
		list[index] = input["Value"]
		output["List"] = list
		return output
		
	def setSocketType(self, type):
		self.inputs.clear()
		self.outputs.clear()
		if type == "FLOAT":
			self.inputs.new("FloatListSocket", "List")
			self.inputs.new("FloatSocket", "Value")
			self.inputs.new("IntegerSocket", "Index")
			self.outputs.new("FloatListSocket", "List")
		elif type == "STRING":
			self.inputs.new("StringListSocket", "List")
			self.inputs.new("StringSocket", "Value")
			self.inputs.new("IntegerSocket", "Index")
			self.outputs.new("StringListSocket", "List")
		elif type == "OBJECT":
			self.inputs.new("ObjectListSocket", "List")
			self.inputs.new("ObjectSocket", "Value")
			self.inputs.new("IntegerSocket", "Index")
			self.outputs.new("ObjectListSocket", "List")
