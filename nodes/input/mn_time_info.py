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
		allowCompiling()
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Frame" : "frame"}
		
	def execute(self):
		return getCurrentFrame()