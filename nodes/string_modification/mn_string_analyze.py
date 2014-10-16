import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_StringAnalyzeNode(Node, AnimationNode):
	bl_idname = "mn_StringAnalyzeNode"
	bl_label = "Text Analyze"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("StringSocket", "Text")
		self.outputs.new("IntegerSocket", "Length")
		allowCompiling()
		
	def execute(self, input):
		output = {}
		output["Length"] = len(input["Text"])
		return output