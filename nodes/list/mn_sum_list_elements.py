import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class SumListElementsNode(Node, AnimationNode):
	bl_idname = "SumListElementsNode"
	bl_label = "Sum Elements"
	
	def setSocketTypes(self, context):
		self.setSocketType(self.listTypesProperty)	
		nodePropertyChanged(self, context)
	
	listTypes = [
		("FLOAT", "Float", ""),
		("STRING", "String", "")]
	listTypesProperty = bpy.props.EnumProperty(name = "Type", items = listTypes, default = "FLOAT", update = setSocketTypes)
	
	def init(self, context):
		self.setSocketType(self.listTypesProperty)
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "listTypesProperty")
		
	def execute(self, input):
		output = {}
		list = input["List"]
		type = self.listTypesProperty
		
		start = clampInt(input["Start"], 0, len(list))
		end = clampInt(input["End"], 0, len(list))
		
		if type == "FLOAT":
			output["Sum"] = 0.0
			for i in range(start, end):
				output["Sum"] += list[i]
		elif type == "STRING":
			output["Sum"] = "".join(list)
		
		return output
		
	def setSocketType(self, type):
		self.inputs.clear()
		self.outputs.clear()
		if type == "FLOAT":
			self.inputs.new("FloatListSocket", "List")
			self.inputs.new("IntegerSocket", "Start")
			self.inputs.new("IntegerSocket", "End")
			self.outputs.new("FloatSocket", "Sum")
		elif type == "STRING":
			self.inputs.new("StringListSocket", "List")
			self.inputs.new("IntegerSocket", "Start")
			self.inputs.new("IntegerSocket", "End")
			self.outputs.new("StringSocket", "Sum")