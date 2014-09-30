import bpy
from bpy.types import Node
from mn_node_helper import AnimationNode
from mn_execution import nodePropertyChanged

class ToStringConversion(Node, AnimationNode):
	bl_idname = "ToStringConversion"
	bl_label = "To String"
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Value")
		self.outputs.new("StringSocket", "Text")
		
	def execute(self, input):
		output = {}
		output["Text"] = str(input["Value"])
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)