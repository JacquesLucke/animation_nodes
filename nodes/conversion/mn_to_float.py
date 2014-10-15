import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class ToFloatConversion(Node, AnimationNode):
	bl_idname = "ToFloatConversion"
	bl_label = "To Float"
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Value")
		self.outputs.new("FloatSocket", "Number")
		
	def getInputSocketNames(self):
		return {"Value" : "value"}
	def getOutputSocketNames(self):
		return {"Number" : "number"}
		
	def execute(self, value):
		return float(value)