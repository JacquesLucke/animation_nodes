import bpy
from bpy.types import Node
from animation_nodes.mn_cache import getUniformRandom
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_interpolation_utils import *

class mn_AnimateFloatNode(Node, AnimationNode):
	bl_idname = "mn_AnimateFloatNode"
	bl_label = "Animate Number"
	outputUseParameterName = "useOutput"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "Start")
		self.inputs.new("mn_FloatSocket", "End")
		self.inputs.new("mn_FloatSocket", "Time")
		self.inputs.new("mn_InterpolationSocket", "Interpolation").showName = False
		self.inputs.new("mn_FloatSocket", "Duration").number = 20.0
		self.inputs.new("mn_FloatSocket", "Delay").number = 0.0
		self.outputs.new("mn_FloatSocket", "Current")
		self.outputs.new("mn_FloatSocket", "New Time")
		self.outputs.new("mn_FloatSocket", "Difference")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def getInputSocketNames(self):
		return {"Start" : "start", "End" : "end", "Time" : "time", "Interpolation" : "interpolation", "Duration" : "duration", "Delay" : "delay"}
	def getOutputSocketNames(self):
		return {"Current" : "current", "New Time" : "newTime", "Difference" : "difference"}
		
	def execute(self, useOutput, start, end, time, interpolation, duration, delay):
		duration = max(duration, 1)
		influence = interpolation[0](max(min(time / duration, 1.0), 0.0), interpolation[1])
		current = start * (1 - influence) + end * influence
		difference = 0
		if useOutput["Difference"]:
			influence = interpolation[0](max(min((time - 1)/ duration, 1.0), 0.0), interpolation[1])
			oldResult = start * (1 - influence) + end * influence
			difference = current - oldResult
		return current, time - duration - delay, difference
		

classes = [
	mn_AnimateFloatNode
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
