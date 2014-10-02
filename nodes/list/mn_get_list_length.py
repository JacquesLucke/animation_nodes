import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class GetListLengthNode(Node, AnimationNode):
	bl_idname = "GetListLengthNode"
	bl_label = "Get List Length"
	
	def init(self, context):
		self.inputs.new("GenericSocket", "List")
		self.outputs.new("IntegerSocket", "Length")
		
	def execute(self, input):
		output = {}
		output["Length"] = len(input["List"])
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)