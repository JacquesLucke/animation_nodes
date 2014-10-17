import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_StringInputNode(Node, AnimationNode):
	bl_idname = "mn_StringInputNode"
	bl_label = "Text Input"
	
	stringProperty = bpy.props.StringProperty(default = "text", update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_StringSocket", "Text")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "stringProperty", text = "")
		
	def execute(self, input):
		output = {}
		output["Text"] = self.stringProperty
		return output