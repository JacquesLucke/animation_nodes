import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class SubProgramStartNode(Node, AnimationNode):
	bl_idname = "SubProgramStartNode"
	bl_label = "Sub-Program Start"
	
	def init(self, context):
		self.outputs.new("SubProgramSocket", "Sub-Program")
		self.outputs.new("ObjectListSocket", "Objects")
		self.outputs.new("IntegerSocket", "Index")
		
	def execute(self, input):
		return input
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)