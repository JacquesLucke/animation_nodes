import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class CombineVector(Node, AnimationNode):
	bl_idname = "CombineVector"
	bl_label = "Combine Vector"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("FloatSocket", "X")
		self.inputs.new("FloatSocket", "Y")
		self.inputs.new("FloatSocket", "Z")
		self.outputs.new("VectorSocket", "Vector")
		allowCompiling()
		
	def getSocketVariableConnections(self):
		return ({"X" : "x", "Y" : "y", "Z" : "z"}, {"Vector" : "vector"})
		
	def execute(self, x, y, z):
		return [x, y, z]
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)