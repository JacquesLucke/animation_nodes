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
		
	def getInputSocketNames(self):
		return {"Vector" : "vector"}
	def getOutputSocketNames(self):
		return {"X" : "x",
				"Y" : "y",
				"Z" : "z"}
		
	def execute(self, vector):
		return vector[0], vector[1], vector[2]
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)