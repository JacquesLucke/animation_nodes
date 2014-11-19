import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_SumListElementsNode(Node, AnimationNode):
	bl_idname = "mn_SumListElementsNode"
	bl_label = "Sum Elements"
	
	def setSocketTypes(self, context):
		self.setSocketType(self.listTypesProperty)	
		nodePropertyChanged(self, context)
	
	listTypes = [
		("FLOAT", "Float", ""),
		("STRING", "String", "")]
	listTypesProperty = bpy.props.EnumProperty(name = "Type", items = listTypes, default = "FLOAT", update = setSocketTypes)
	
	def init(self, context):
		forbidCompiling()
		self.setSocketType(self.listTypesProperty)
		allowCompiling()
		
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
		forbidCompiling()
		self.inputs.clear()
		self.outputs.clear()
		if type == "FLOAT":
			self.inputs.new("mn_FloatListSocket", "List")
			self.inputs.new("mn_IntegerSocket", "Start")
			self.inputs.new("mn_IntegerSocket", "End")
			self.outputs.new("mn_FloatSocket", "Sum")
		elif type == "STRING":
			self.inputs.new("mn_StringListSocket", "List")
			self.inputs.new("mn_IntegerSocket", "Start")
			self.inputs.new("mn_IntegerSocket", "End")
			self.outputs.new("mn_StringSocket", "Sum")
		allowCompiling()

