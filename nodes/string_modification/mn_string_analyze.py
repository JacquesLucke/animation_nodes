import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class StringAnalyzeNode(Node, AnimationNode):
	bl_idname = "StringAnalyzeNode"
	bl_label = "Text Analyze"
	
	def init(self, context):
		self.inputs.new("StringSocket", "Text")
		self.outputs.new("IntegerSocket", "Length")
		
	def execute(self, input):
		output = {}
		output["Length"] = len(input["Text"])
		return output