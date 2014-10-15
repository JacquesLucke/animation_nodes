import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class ToStringConversion(Node, AnimationNode):
	bl_idname = "ToStringConversion"
	bl_label = "To String"
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Value")
		self.outputs.new("StringSocket", "Text")
		
	def getInputSocketNames(self):
		return {"Value" : "value"}
	def getOutputSocketNames(self):
		return {"Text" : "text"}
		
	def execute(self, value):
		return str(value)