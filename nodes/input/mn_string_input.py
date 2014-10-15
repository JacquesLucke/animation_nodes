import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class StringInputNode(Node, AnimationNode):
	bl_idname = "StringInputNode"
	bl_label = "String"
	
	stringProperty = bpy.props.StringProperty(default = "text", update = nodePropertyChanged)
	
	def init(self, context):
		self.outputs.new("StringSocket", "Text")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "stringProperty", text = "")
		
	def execute(self, input):
		output = {}
		output["Text"] = self.stringProperty
		return output