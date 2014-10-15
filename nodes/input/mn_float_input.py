import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class FloatInputNode(Node, AnimationNode):
	bl_idname = "FloatInputNode"
	bl_label = "Float"
	
	floatProperty = bpy.props.FloatProperty(default = 0.0, update = nodePropertyChanged)
	
	def init(self, context):
		self.outputs.new("FloatSocket", "Number")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "floatProperty", text = "")
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Number" : "number"}
		
	def execute(self):
		return self.floatProperty