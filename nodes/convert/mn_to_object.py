import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ToObjectConversion(Node, AnimationNode):
	bl_idname = "mn_ToObjectConversion"
	bl_label = "To Object"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_GenericSocket", "Value")
		self.outputs.new("mn_ObjectSocket", "Object")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Value" : "value"}
	def getOutputSocketNames(self):
		return {"Object" : "object"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		return "$object$ = bpy.data.objects.get(str(%value%))"