import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *

class mn_TimeInfoNode(Node, AnimationNode):
	bl_idname = "mn_TimeInfoNode"
	bl_label = "Time Info"
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("FloatSocket", "Frame")
		self.outputs.new("FloatSocket", "Start Frame")
		self.outputs.new("FloatSocket", "End Frame")
		self.outputs.new("FloatSocket", "Frame Rate")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Frame" : "frame",
				"Start Frame" : "start_frame",
				"End Frame" : "end_frame",
				"Frame Rate" : "frame_rate"}
		
	def execute(self):
		scene = bpy.context.scene
		return getCurrentFrame(), scene.frame_start, scene.frame_end, scene.render.fps