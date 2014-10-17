import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_IntegerInputNode(Node, AnimationNode):
	bl_idname = "mn_IntegerInputNode"
	bl_label = "Integer Input"
	
	intProperty = bpy.props.IntProperty(default = 0, update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_IntegerSocket", "Number")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "intProperty", text = "")
		
	def execute(self, input):
		output = {}
		output["Number"] = self.intProperty
		return output