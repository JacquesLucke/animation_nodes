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
		self.inputs.new("mn_FloatSocket", "Movement Time").number = 1.0
		self.inputs.new("mn_FloatSocket", "Stay Time").number = 0.0
		self.outputs.new("mn_FloatSocket", "New Value")
		self.outputs.new("mn_VectorSocket", "Vector")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def getInputSocketNames(self):
		return {"Value" : "value", "A" : "a", "B" : "b", "Movement Time" : "moveTime", "Stay Time" : "stayTime"}
	def getOutputSocketNames(self):
		return {"Vector" : "vector", "New Value" : "newValue"}
		
	def execute(self, value, a, b, moveTime, stayTime):
		value /= moveTime
		influence = getBackOutNormalInfluence(max(min(value, 1.0), 0.0))
		newVector = [a[0] * (1 - influence) + b[0] * influence,
					a[1] * (1 - influence) + b[1] * influence,
					a[2] * (1 - influence) + b[2] * influence]
		return value * moveTime - moveTime - stayTime, newVector
		