import bpy
from bpy.types import Node
from mn_cache import getUniformRandom
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_interpolation_utils import *

class mn_AnimateFloatNode(Node, AnimationNode):
	bl_idname = "mn_AnimateFloatNode"
	bl_label = "Animate Number"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "A")
		self.inputs.new("mn_FloatSocket", "B")
		self.inputs.new("mn_FloatSocket", "Time")
		self.inputs.new("mn_InterpolationSocket", "Interpolation")
		self.inputs.new("mn_FloatSocket", "Movement Time").number = 20.0
		self.inputs.new("mn_FloatSocket", "Stay Time").number = 0.0
		self.outputs.new("mn_FloatSocket", "Result")
		self.outputs.new("mn_FloatSocket", "New Time")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def getInputSocketNames(self):
		return {"A" : "a", "B" : "b", "Time" : "time", "Interpolation" : "interpolation", "Movement Time" : "moveTime", "Stay Time" : "stayTime"}
	def getOutputSocketNames(self):
		return {"Result" : "result", "New Time" : "newTime"}
		
	def execute(self, a, b, time, interpolation, moveTime, stayTime):
		influence = interpolation[0](max(min(time / moveTime, 1.0), 0.0), interpolation[1])
		result = a * (1 - influence) + b * influence
		return result, time - moveTime - stayTime
		