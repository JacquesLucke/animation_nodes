import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class CombineListsNode(Node, AnimationNode):
	bl_idname = "CombineListsNode"
	bl_label = "Combine Lists"
	
	def init(self, context):
		self.inputs.new("FloatListSocket", "List 1")
		self.inputs.new("FloatListSocket", "List 2")
		self.outputs.new("FloatListSocket", "Both Lists")
		
	def execute(self, input):
		output = {}
		combination = input["List 1"][:]
		combination.extend(input["List 2"])
		output["Both Lists"] = combination
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)