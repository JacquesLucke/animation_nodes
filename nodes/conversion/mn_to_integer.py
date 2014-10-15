import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class ToIntegerConversion(Node, AnimationNode):
	bl_idname = "ToIntegerConversion"
	bl_label = "To Integer"
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Value")
		self.outputs.new("IntegerSocket", "Number")
		
	def getInputSocketNames(self):
		return {"Value" : "value"}
	def getOutputSocketNames(self):
		return {"Number" : "number"}
		
	def execute(self, value):
		return int(value)