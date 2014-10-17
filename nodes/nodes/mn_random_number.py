import bpy, random
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_RandomNumberNode(Node, AnimationNode):
	bl_idname = "mn_RandomNumberNode"
	bl_label = "Random Number"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Seed")
		self.inputs.new("mn_FloatSocket", "Min").number = 0.0
		self.inputs.new("mn_FloatSocket", "Max").number = 1.0
		self.outputs.new("mn_FloatSocket", "Float Value")
		self.outputs.new("mn_IntegerSocket", "Integer Value")
		allowCompiling()
		
	def execute(self, input):
		output = {}
		seed = input["Seed"]
		min = input["Min"]
		max = input["Max"]
		random.seed(seed)
		output["Float Value"] = random.uniform(min, max)
		output["Integer Value"] = int(output["Float Value"])
		return output