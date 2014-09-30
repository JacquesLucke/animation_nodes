import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class ReplicateStringsNode(Node, AnimationNode):
	bl_idname = "ReplicateStringsNode"
	bl_label = "Replicate Strings"
	
	def init(self, context):
		self.inputs.new("StringSocket", "Text")
		self.inputs.new("IntegerSocket", "Amount")
		self.outputs.new("StringSocket", "Text")
		
	def execute(self, input):
		output = {}
		output["Text"] = input["Text"] * input["Amount"]
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)