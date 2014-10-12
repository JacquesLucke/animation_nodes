import bpy, random
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class RandomStringNode(Node, AnimationNode):
	bl_idname = "RandomStringNode"
	bl_label = "Random Text"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("IntegerSocket", "Seed")
		self.inputs.new("IntegerSocket", "Length").number = 5
		self.inputs.new("StringSocket", "Characters").string = "abcdefghijklmnopqrstuvwxyz"
		self.outputs.new("StringSocket", "Text")
		allowCompiling()
		
	def execute(self, input):
		output = {}
		seed = input["Seed"]
		length = input["Length"]
		characters = input["Characters"]
		random.seed(seed)
		output["Text"] = ''.join(random.choice(characters) for _ in range(length))
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)