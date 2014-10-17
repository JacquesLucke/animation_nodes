import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ToIntegerConversion(Node, AnimationNode):
	bl_idname = "mn_ToIntegerConversion"
	bl_label = "To Integer"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_GenericSocket", "Value")
		self.outputs.new("mn_IntegerSocket", "Number")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Value" : "value"}
	def getOutputSocketNames(self):
		return {"Number" : "number"}
		
	def execute(self, value):
		return int(value)