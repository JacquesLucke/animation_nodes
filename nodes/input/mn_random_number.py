import bpy, random
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class RandomNumberNode(Node, AnimationNode):
	bl_idname = "RandomNumberNode"
	bl_label = "Random Number"
	
	def init(self, context):
		self.inputs.new("IntegerSocket", "Seed")
		self.inputs.new("FloatSocket", "Min").number = 0.0
		self.inputs.new("FloatSocket", "Max").number = 1.0
		self.outputs.new("FloatSocket", "Float Value")
		self.outputs.new("IntegerSocket", "Integer Value")
		
	def execute(self, input):
		output = {}
		seed = input["Seed"]
		min = input["Min"]
		max = input["Max"]
		random.seed(seed)
		output["Float Value"] = random.uniform(min, max)
		output["Integer Value"] = int(output["Float Value"])
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)