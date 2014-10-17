import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ToStringConversion(Node, AnimationNode):
	bl_idname = "mn_ToStringConversion"
	bl_label = "To String"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_GenericSocket", "Value")
		self.outputs.new("mn_StringSocket", "Text")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Value" : "value"}
	def getOutputSocketNames(self):
		return {"Text" : "text"}
		
	def execute(self, value):
		return str(value)