import bpy
from bpy.types import Node
from mn_node_helper import AnimationNode
from mn_execution import nodePropertyChanged

class CombineVector(Node, AnimationNode):
	bl_idname = "CombineVector"
	bl_label = "Combine Vector"
	
	def init(self, context):
		self.inputs.new("FloatSocket", "X")
		self.inputs.new("FloatSocket", "Y")
		self.inputs.new("FloatSocket", "Z")
		self.outputs.new("VectorSocket", "Vector")
		
	def execute(self, input):
		output = {}
		output["Vector"] = (input["X"], input["Y"], input["Z"])
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)