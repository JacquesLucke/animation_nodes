import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_StringAnalyzeNode(Node, AnimationNode):
	bl_idname = "mn_StringAnalyzeNode"
	bl_label = "Text Analyze"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_StringSocket", "Text")
		self.outputs.new("mn_IntegerSocket", "Length")
		allowCompiling()
		
	def execute(self, input):
		output = {}
		output["Length"] = len(input["Text"])
		return output

