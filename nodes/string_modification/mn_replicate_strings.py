import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class ReplicateStringsNode(Node, AnimationNode):
	bl_idname = "ReplicateStringsNode"
	bl_label = "Replicate Strings"
	
	def init(self, context):
		self.inputs.new("StringSocket", "Text")
		self.inputs.new("IntegerSocket", "Amount")
		self.outputs.new("StringSocket", "Text")
		
	def execute(self, input):
		output = {}
		output["Text"] = input["Text"] * input["Amount"]
		return output