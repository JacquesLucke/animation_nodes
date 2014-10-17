import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_FloatInputNode(Node, AnimationNode):
	bl_idname = "mn_FloatInputNode"
	bl_label = "Number Input"
	
	floatProperty = bpy.props.FloatProperty(default = 0.0, update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_FloatSocket", "Number")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "floatProperty", text = "")
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Number" : "number"}
		
	def execute(self):
		return self.floatProperty