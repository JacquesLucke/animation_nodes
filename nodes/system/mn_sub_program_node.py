import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class SubProgramNode(Node, AnimationNode):
	bl_idname = "SubProgramNode"
	bl_label = "Sub-Program"
	
	def init(self, context):
		self.inputs.new("SubProgramSocket", "Sub-Program")
		self.inputs.new("ObjectListSocket", "Objects")
		self.outputs.new("ObjectListSocket", "Objects")
		
	def execute(self, input):
		return input
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)