import bpy, random
from mn_math_utils import perlinNoise
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_FloatClamp(Node, AnimationNode):
	bl_idname = "mn_FloatClamp"
	bl_label = "Clamp"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "Value")
		self.inputs.new("mn_FloatSocket", "Min").number = 0.0
		self.inputs.new("mn_FloatSocket", "Max").number = 1.0
		self.outputs.new("mn_FloatSocket", "Value")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Value" : "value",
				"Min" : "minValue",
				"Max" : "maxValue"}
	def getOutputSocketNames(self):
		return {"Value" : "value"}

	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self):
		return "$value$ = min(max(%value%, %minValue%), %maxValue%)"
		
