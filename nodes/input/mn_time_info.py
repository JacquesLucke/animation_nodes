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
	
	def getSocketVariableConnections(self):
		return ({}, {"Frame" : "frame"})
		
	def execute(self):
		return getCurrentFrame()
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)