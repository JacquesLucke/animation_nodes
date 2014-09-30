import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class ToFloatConversion(Node, AnimationNode):
	bl_idname = "ToFloatConversion"
	bl_label = "To Float"
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Value")
		self.outputs.new("FloatSocket", "Number")
		
	def execute(self, input):
		output = {}
		output["Number"] = str(input["Value"])
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)