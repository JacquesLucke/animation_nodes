import bpy
from bpy.types import Node
from mn_cache import getUniformRandom
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_interpolation_utils import *

class mn_AnimateVectorNode(Node, AnimationNode):
	bl_idname = "mn_AnimateVectorNode"
	bl_label = "Animate Vector"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VectorSocket", "Start")
		self.inputs.new("mn_VectorSocket", "End")
		self.inputs.new("mn_FloatSocket", "Time")
		self.inputs.new("mn_InterpolationSocket", "Interpolation")
		self.inputs.new("mn_FloatSocket", "Movement Time").number = 20.0
		self.inputs.new("mn_FloatSocket", "Stay Time").number = 0.0
		self.outputs.new("mn_VectorSocket", "Vector")
		self.outputs.new("mn_FloatSocket", "New Time")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def getInputSocketNames(self):
		return {"Start" : "start", "End" : "end", "Time" : "time", "Interpolation" : "interpolation", "Movement Time" : "moveTime", "Stay Time" : "stayTime"}
	def getOutputSocketNames(self):
		return {"Vector" : "vector", "New Time" : "newTime"}
		
	def execute(self, start, end, time, interpolation, moveTime, stayTime):
		influence = interpolation[0](max(min(time / moveTime, 1.0), 0.0), interpolation[1])
		newVector = [start[0] * (1 - influence) + end[0] * influence,
					start[1] * (1 - influence) + end[1] * influence,
					start[2] * (1 - influence) + end[2] * influence]
		return newVector, time - moveTime - stayTime
		