import bpy, random
from mn_math_utils import perlinNoise
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_GridArrange(Node, AnimationNode):
	bl_idname = "mn_GridArrange"
	bl_label = "Grid Arrange"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Index")
		self.inputs.new("mn_IntegerSocket", "Width").number = 10
		self.inputs.new("mn_FloatSocket", "Distance").number = 3
		self.outputs.new("mn_VectorSocket", "Vector")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Index" : "index",
				"Width" : "width",
				"Distance" : "distance"}
	def getOutputSocketNames(self):
		return {"Vector" : "vector"}

	def execute(self, index, width, distance):
		width = max(width, 1)
		vector = [0, 0, 0]
		vector[0] = index % width * distance
		vector[1] = int(index / width) * distance
		return vector
		
