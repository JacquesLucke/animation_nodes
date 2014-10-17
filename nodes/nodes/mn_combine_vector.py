import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_CombineVector(Node, AnimationNode):
	bl_idname = "mn_CombineVector"
	bl_label = "Combine Vector"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "X")
		self.inputs.new("mn_FloatSocket", "Y")
		self.inputs.new("mn_FloatSocket", "Z")
		self.outputs.new("mn_VectorSocket", "Vector")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"X" : "x",
				"Y" : "y",
				"Z" : "z"}
	def getOutputSocketNames(self):
		return {"Vector" : "vector"}
		
	def execute(self, x, y, z):
		return [x, y, z]