import bpy
from bpy.types import Node
from mn_cache import getUniformRandom
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_interpolation_utils import *

class mn_MixVectorNode(Node, AnimationNode):
	bl_idname = "mn_MixVectorNode"
	bl_label = "Mix Vector"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "Value")
		self.inputs.new("mn_VectorSocket", "A")
		self.inputs.new("mn_VectorSocket", "B")
		self.inputs.new("mn_FloatSocket", "Subtract").number = 1.0
		self.outputs.new("mn_VectorSocket", "Vector")
		self.outputs.new("mn_FloatSocket", "Subtracted Value")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def getInputSocketNames(self):
		return {"Value" : "value", "A" : "a", "B" : "b", "Subtract" : "subtract"}
	def getOutputSocketNames(self):
		return {"Vector" : "vector", "Subtracted Value" : "newValue"}
		
	def execute(self, value, a, b, subtract):
		influence = getBackOutNormalInfluence(max(min(value, 1.0), 0.0))
		return [a[0] * (1 - influence) + b[0] * influence,
				a[1] * (1 - influence) + b[1] * influence,
				a[2] * (1 - influence) + b[2] * influence], value - subtract
		