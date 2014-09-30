import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class SeparateVector(Node, AnimationNode):
	bl_idname = "SeparateVector"
	bl_label = "Separate Vector"
	
	def init(self, context):
		self.inputs.new("VectorSocket", "Vector")
		self.outputs.new("FloatSocket", "X")
		self.outputs.new("FloatSocket", "Y")
		self.outputs.new("FloatSocket", "Z")
		
	def execute(self, input):
		output = {}
		output["X"]= input["Vector"][0]
		output["Y"]= input["Vector"][1]
		output["Z"]= input["Vector"][2]
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)