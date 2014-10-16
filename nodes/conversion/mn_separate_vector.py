import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_SeparateVector(Node, AnimationNode):
	bl_idname = "mn_SeparateVector"
	bl_label = "Separate Vector"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("VectorSocket", "Vector")
		self.outputs.new("FloatSocket", "X")
		self.outputs.new("FloatSocket", "Y")
		self.outputs.new("FloatSocket", "Z")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Vector" : "vector"}
	def getOutputSocketNames(self):
		return {"X" : "x",
				"Y" : "y",
				"Z" : "z"}
		
	def execute(self, vector):
		return vector[0], vector[1], vector[2]