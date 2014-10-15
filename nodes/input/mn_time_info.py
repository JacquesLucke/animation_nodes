import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class TimeInfoNode(Node, AnimationNode):
	bl_idname = "TimeInfoNode"
	bl_label = "Time Info"
	
	def init(self, context):
		self.outputs.new("FloatSocket", "Frame")
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Frame" : "frame"}
		
	def execute(self):
		return getCurrentFrame()