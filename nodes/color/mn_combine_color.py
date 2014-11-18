import bpy, random
from animation_nodes.utils.mn_math_utils import perlinNoise
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_CombineColor(Node, AnimationNode):
	bl_idname = "mn_CombineColor"
	bl_label = "Combine Color"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "Red")
		self.inputs.new("mn_FloatSocket", "Green")
		self.inputs.new("mn_FloatSocket", "Blue")
		self.inputs.new("mn_FloatSocket", "Alpha").number = 1
		self.outputs.new("mn_ColorSocket", "Color")
		allowCompiling()

	def getInputSocketNames(self):
		return {"Red" : "red",
				"Green" : "green",
				"Blue" : "blue",
				"Alpha" : "alpha"}
	def getOutputSocketNames(self):
		return {"Color" : "color"}

	def execute(self, red, green, blue, alpha):
		return [red, green, blue, alpha] 
		


