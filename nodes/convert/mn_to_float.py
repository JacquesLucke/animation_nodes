import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ToFloatConversion(Node, AnimationNode):
	bl_idname = "mn_ToFloatConversion"
	bl_label = "To Float"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_GenericSocket", "Value")
		self.outputs.new("mn_FloatSocket", "Number")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Value" : "value"}
	def getOutputSocketNames(self):
		return {"Number" : "number"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		return "$number$ = float(%value%)"